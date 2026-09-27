"""Receipt-backed trajectory and review audit; no model calls or controller feedback."""
from argparse import ArgumentParser
from collections import Counter
from hashlib import sha256
from pathlib import Path
import json
from horus.live import SessionStore,_atomic_write
from experiments.modern_memory_vs_horus_v0.storage import ModernMemory,file_hash
from grounded_state import AuthenticatedMemory,RelationKey,derive_relation_state
from .protocol import RUNS,DECISIONS,REVIEW_EVERY,ACTIONS,RESTART_RUN,relation_type
from .worker import rows_of,state_view

def read(path):return json.loads(path.read_text())
def prior_state(rows,relation,sequence):
    from grounded_state import deterministic,empirical
    relevant=[r for r in rows if r['relation']==relation and r['event_stream_sequence']<sequence]
    kind=relation_type(relation)
    evidence=(empirical.fold(relevant) if kind.value=='EMPIRICAL' else deterministic.fold(relevant))
    from grounded_state.core import DerivedRelationState,ReceiptProvenance
    provenance=tuple(ReceiptProvenance(p['identity'],p['receipt_sha256'],p['event_stream_sequence'],
        p['value']['next_state'],p['value']['consequence']) for p in evidence['receipt_provenance'])
    state=DerivedRelationState(RelationKey(int(relation.split(':')[0]),relation.split(':')[1]),kind,
        evidence['kind'],json.dumps(evidence,sort_keys=True,separators=(',',':')),provenance)
    return state_view(state)

def analyze_run(root,run):
    path=root/'runs'/run
    with SessionStore(path/'session',True) as store,ModernMemory(path/'memory.sqlite3',False) as memory:
        memory.reconcile(store);all_memory=memory.rows()
        decisions=rows_of(store,'AUTONOMOUS_AGENT_DECISION')
        reviews=rows_of(store,'SELF_REVIEW_NON_AUTHORITATIVE')
        if len(decisions)!=DECISIONS or len(reviews)!=DECISIONS//REVIEW_EVERY:
            raise RuntimeError('INVALID: incomplete run or review cadence')
        if len(store.records['events'])!=DECISIONS or len(all_memory)!=DECISIONS:
            raise RuntimeError('INVALID: missing authenticated receipt')
        for index,d in enumerate(decisions,1):
            if d['index']!=index or d['decision_id']!=f'{run}:D{index:02d}' or d['selected_action'] not in ACTIONS or d['action_parse_status']!='VALID':
                raise RuntimeError('INVALID: decision sequence or action')
            event=store.records['events'][index-1]['record'];receipt=event['receipt']
            if event['decision_index']!=index or receipt['pre_state']!=d['state'] or receipt['action']!=d['selected_action']:
                raise RuntimeError('INVALID: decision/action/receipt mismatch')
            if d['realized']!=dict(next_state=receipt['next_state'],consequence=receipt['realized_consequence']):
                raise RuntimeError('INVALID: realized consequence mismatch')
            if d['receipt_provenance_sha256']!=event['receipt_provenance_sha256'] or d['event_stream_sequence']!=index:
                raise RuntimeError('INVALID: receipt provenance mismatch')
            for action in ACTIONS:
                relation=f"{d['state']}:{action}"
                expected=prior_state(all_memory,relation,index)
                if d['grounded_assessments_before'][action]!=expected:
                    raise RuntimeError('INVALID: pre-decision grounded assessment mismatch')
            relation=f"{d['state']}:{d['selected_action']}"
            expected_after=prior_state(all_memory,relation,index+1)
            if d['grounded_after']!=expected_after:
                raise RuntimeError('INVALID: post-receipt grounded state mismatch')
        for n,r in enumerate(reviews,1):
            if r['after_decision']!=n*REVIEW_EVERY or r['reviewed_decisions']!=[f'{run}:D{i:02d}' for i in range((n-1)*REVIEW_EVERY+1,n*REVIEW_EVERY+1)]:
                raise RuntimeError('INVALID: review cadence or bounded window')
            if not r['non_authoritative'] or not r['no_memory_or_state_change']:
                raise RuntimeError('INVALID: review gained authority')
            if r['review_status'] not in ('VALID_SELF_REVIEW','INVALID_SELF_REVIEW'):
                raise RuntimeError('INVALID: review status')
            if r['review_status']=='INVALID_SELF_REVIEW' and r['proposal_status'] is not None:
                raise RuntimeError('INVALID: malformed review became proposal')
            if r['review_status']=='VALID_SELF_REVIEW' and r['proposal_status'] not in ('NON_AUTHORITATIVE_SELF_PROPOSAL','NO_CHANGE_PROPOSED'):
                raise RuntimeError('INVALID: valid review has wrong proposal status')
        if run==RESTART_RUN:
            if read(path/'restart-verdict.json')['status']!='PASS':
                raise RuntimeError('INVALID: restart verdict')
        calls=[x['record'] for x in store.records['calls'] if x['kind']=='REQUEST_INTENT']
        model_calls=len(calls)
        recorded_calls=sum(bool(d['model_call_id']) for d in decisions)+sum(bool(r['model_call_id']) for r in reviews)
        if model_calls<recorded_calls:raise RuntimeError('INVALID: missing model call intent')
        total=sum(d['realized']['consequence'] for d in decisions)
        unseen=sum(d['selected_grounded_before']['kind']=='UNSEEN' for d in decisions)
        repeated_negative=0;established_reliance=0;unresolved=0;empirical_certainty_claims=0
        for d in decisions:
            selected=d['selected_grounded_before'];e=selected.get('established_value')
            if e and e['consequence']<0:repeated_negative+=1
            elif selected['relation_type']=='EMPIRICAL' and any(int(k.split(':')[1])<0 for k in selected['segment_counts']):
                repeated_negative+=1
            if selected['kind']=='ESTABLISHED' and d['stated_reliance']=='GROUNDED':established_reliance+=1
            if selected['assessment_status']=='UNRESOLVED':unresolved+=1
            if selected['relation_type']=='EMPIRICAL' and d['claimed_consequence'] is not None and selected['kind']=='VARIABLE_RELATION':
                empirical_certainty_claims+=1
        change_events=[d for d in decisions if d['grounded_state_change']['before_kind']!=d['grounded_state_change']['after_kind']]
        adaptation=[]
        for d in change_events:
            following=next((x for x in decisions[d['index']:] if x['state']==d['state']),None)
            adaptation.append(dict(trigger_decision=d['decision_id'],change=d['grounded_state_change'],
                next_same_state_decision=None if following is None else following['decision_id'],
                latency_decisions=None if following is None else following['index']-d['index'],
                action_changed=None if following is None else following['selected_action']!=d['selected_action']))
        timeline=[f"{d['decision_id']} state={d['state']} {d['selected_action']} "
            f"{d['selected_grounded_before']['kind']} → {d['realized']['consequence']:+d}, "
            f"next={d['realized']['next_state']}, after={d['grounded_after']['kind']} "
            f"reason={d['agent_reason']}" for d in decisions]
        review_summary=[dict(review_id=r['review_id'],after_decision=r['after_decision'],
            proposal_status=r['proposal_status'],review_status=r['review_status'],
            SELF_REVIEW=r['SELF_REVIEW'],raw_model_output_sha256=r['raw_model_output_sha256'],
            reviewed_decisions=r['reviewed_decisions'],no_memory_or_state_change=r['no_memory_or_state_change'],
            model_call_id=r['model_call_id'],context_tokens=r['context_tokens']) for r in reviews]
        metrics=dict(total_realized_consequence=total,decisions=len(decisions),
            unique_relations_encountered=len({f"{d['state']}:{d['selected_action']}" for d in decisions}),
            unseen_relations_explored=unseen,repeated_negative_grounded_actions=repeated_negative,
            decisions_relying_on_established_evidence=established_reliance,
            decisions_despite_unresolved_evidence=unresolved,
            agent_grounded_state_disagreements=sum(bool(d['agent_grounded_state_disagreement']) for d in decisions),
            empirical_variable_point_claims=empirical_certainty_claims,
            incomplete_descriptive_outputs=sum(d['descriptive_status']=='INCOMPLETE_DESCRIPTIVE_OUTPUT' for d in decisions),
            invalid_descriptive_outputs=sum(d['descriptive_status']=='INVALID_DESCRIPTIVE_OUTPUT' for d in decisions),
            invalid_self_reviews=sum(r['review_status']=='INVALID_SELF_REVIEW' for r in reviews),
            model_calls=model_calls,decision_model_calls=sum(c['role']=='DECISION' for c in calls),
            review_model_calls=sum(c['role']=='SELF_REVIEW' for c in calls),
            context_tokens=sum(d['context_tokens'] for d in decisions)+sum(r['context_tokens'] for r in reviews),
            grounded_memory_events=memory.checkpoint()['event_count'],grounded_memory_bytes=(path/'memory.sqlite3').stat().st_size)
        return dict(status='PASS',run=run,metrics=metrics,adaptation=adaptation,
            reviews=review_summary,decisions=decisions,timeline=timeline,
            private_files_sha256={p.name:file_hash(p) for p in (path/'session').iterdir() if p.is_file() and p.name!='.lock'},
            memory_sha256=file_hash(path/'memory.sqlite3'),
            restart='PASS' if run==RESTART_RUN else 'NOT_APPLICABLE')

def analyze(root):
    runs={run:analyze_run(root,run) for run in RUNS}
    total_calls=sum(v['metrics']['model_calls'] for v in runs.values())
    result=dict(status='COMPLETE',runs=runs,total_model_calls=total_calls,
        observational_question='Can the agent use authenticated experience to identify weaknesses in its own decision process and propose evidence-grounded improvements without being allowed to change itself?',
        interpretation='PENDING_INDEPENDENT_SELF_REVIEW_AUDIT')
    _atomic_write(root/'analysis.json',result)
    return result

if __name__=='__main__':
    p=ArgumentParser();p.add_argument('--private-root',required=True,type=Path)
    a=p.parse_args();x=analyze(a.private_root)
    print(json.dumps(dict(status=x['status'],total_model_calls=x['total_model_calls'],
        runs={k:v['metrics'] for k,v in x['runs'].items()}),indent=2,sort_keys=True))
