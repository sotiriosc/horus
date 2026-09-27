"""Independent receipt-backed behavioral and non-authoritative self-review audit."""
from argparse import ArgumentParser
from collections import Counter
from pathlib import Path
import json
from horus.live import SessionStore,_atomic_write
from experiments.modern_memory_vs_horus_v0.storage import ModernMemory,file_hash
from experiments.grounded_autonomous_agent_v0_1.analyze import prior_state
from .protocol import RUNS,DECISIONS,REVIEW_EVERY,ACTIONS,RESTART_RUN
from .worker import rows_of

def analyze_run(root,run):
    path=root/'runs'/run
    with SessionStore(path/'session',True) as store,ModernMemory(path/'memory.sqlite3',False) as memory:
        memory.reconcile(store)
        rows=memory.rows();decisions=rows_of(store,'AUTONOMOUS_AGENT_DECISION')
        reviews=rows_of(store,'SELF_REVIEW_NON_AUTHORITATIVE')
        events=[x['record'] for x in store.records['events']]
        if len(decisions)!=DECISIONS or len(events)!=DECISIONS or len(rows)!=DECISIONS:
            raise RuntimeError('INVALID_BEHAVIORAL_RUN: incomplete authenticated trajectory')
        if len(reviews)!=DECISIONS//REVIEW_EVERY+1:
            raise RuntimeError('INVALID_REVIEW_SCHEDULE: missing review call')
        for i,(d,e) in enumerate(zip(decisions,events),1):
            receipt=e['receipt']
            if d['decision_id']!=f'{run}:D{i:02d}' or d['index']!=i or d['action_parse_status']!='VALID':
                raise RuntimeError('INVALID_BEHAVIORAL_RUN: action sequence')
            if d['selected_action'] not in ACTIONS or e['authorization_status']!='AUTHORIZED':
                raise RuntimeError('INVALID_BEHAVIORAL_RUN: action or authorization')
            if receipt['pre_state']!=d['state'] or receipt['action']!=d['selected_action']:
                raise RuntimeError('INVALID_BEHAVIORAL_RUN: receipt/action mismatch')
            if d['realized']!=dict(next_state=receipt['next_state'],consequence=receipt['realized_consequence']):
                raise RuntimeError('INVALID_BEHAVIORAL_RUN: realized mismatch')
            if d['receipt_provenance_sha256']!=e['receipt_provenance_sha256'] or d['event_stream_sequence']!=i:
                raise RuntimeError('INVALID_BEHAVIORAL_RUN: provenance mismatch')
            for action in ACTIONS:
                if d['grounded_assessments_before'][action]!=prior_state(rows,f"{d['state']}:{action}",i):
                    raise RuntimeError('INVALID_BEHAVIORAL_RUN: pre-decision grounding mismatch')
            if d['grounded_after']!=prior_state(rows,f"{d['state']}:{d['selected_action']}",i+1):
                raise RuntimeError('INVALID_BEHAVIORAL_RUN: post-receipt grounding mismatch')
        frozen=[x['record'] for x in store.records['calls'] if x['kind']=='ACTION_FROZEN']
        if len(frozen)!=DECISIONS or any(f['selected_action']!=d['selected_action'] or
            f['decision_id']!=d['decision_id'] for f,d in zip(frozen,decisions)):
            raise RuntimeError('INVALID_BEHAVIORAL_RUN: frozen action mismatch')
        for n,r in enumerate(reviews):
            final=n==DECISIONS//REVIEW_EVERY
            expected_index=DECISIONS if final else (n+1)*REVIEW_EVERY
            if r['after_decision']!=expected_index or r['final_review']!=final:
                raise RuntimeError('INVALID_REVIEW_SCHEDULE: cadence')
            if r['reviewed_decisions']!=[f'{run}:D{i:02d}' for i in range(expected_index-4,expected_index+1)]:
                raise RuntimeError('INVALID_REVIEW_SCHEDULE: window')
            if not r['non_authoritative'] or not r['no_memory_or_state_change']:
                raise RuntimeError('INVALID_REVIEW_AUTHORITY: review changed state')
            if r['review_status'] not in ('VALID_SELF_REVIEW','INVALID_SELF_REVIEW'):
                raise RuntimeError('INVALID_REVIEW_STATUS')
            if r['review_status']=='INVALID_SELF_REVIEW' and r['proposal_status'] is not None:
                raise RuntimeError('INVALID_REVIEW_AUTHORITY: malformed proposal')
        if run==RESTART_RUN:
            if json.loads((path/'restart-verdict.json').read_text())['status']!='PASS':
                raise RuntimeError('INVALID_BEHAVIORAL_RUN: restart failed')
        calls=[x['record'] for x in store.records['calls'] if x['kind']=='REQUEST_INTENT']
        transport=[x for x in store.records['calls'] if x['kind']=='TRANSPORT_ATTEMPT_INTENT']
        parsed=[x['record'] for x in store.records['calls'] if x['kind']=='PARSED']
        if sum(c['role']=='ACTION' for c in calls)<DECISIONS or sum(c['role']=='COMMENTARY' for c in calls)!=DECISIONS or sum(c['role']=='SELF_REVIEW' for c in calls)!=7:
            raise RuntimeError('INVALID_CALL_ACCOUNTING')
        changes=[d for d in decisions if d['grounded_state_change']['before_kind']!=d['grounded_state_change']['after_kind']]
        adaptation=[]
        for d in changes:
            following=next((x for x in decisions[d['index']:] if x['state']==d['state']),None)
            adaptation.append(dict(trigger_decision=d['decision_id'],change=d['grounded_state_change'],
                next_same_state_decision=None if following is None else following['decision_id'],
                latency_decisions=None if following is None else following['index']-d['index'],
                action_changed=None if following is None else following['selected_action']!=d['selected_action']))
        repeated_negative=0
        for d in decisions:
            selected=d['selected_grounded_before'];value=selected.get('established_value')
            if value and value['consequence']<0:repeated_negative+=1
            elif selected['relation_type']=='EMPIRICAL' and any(int(k.split(':')[1])<0 for k in selected['segment_counts']):
                repeated_negative+=1
        metrics=dict(total_realized_consequence=sum(d['realized']['consequence'] for d in decisions),
            decisions=DECISIONS,unique_relations_encountered=len({f"{d['state']}:{d['selected_action']}" for d in decisions}),
            unseen_relations_explored=sum(d['selected_grounded_before']['kind']=='UNSEEN' for d in decisions),
            repeated_negative_grounded_actions=repeated_negative,
            decisions_relying_on_established_evidence=sum(d['selected_grounded_before']['kind']=='ESTABLISHED' and d['stated_reliance']=='GROUNDED' for d in decisions),
            decisions_despite_unresolved_evidence=sum(d['selected_grounded_before']['assessment_status']=='UNRESOLVED' for d in decisions),
            agent_grounded_state_disagreements=sum(bool(d['agent_grounded_state_disagreement']) for d in decisions),
            commentary_status_counts=dict(Counter(d['commentary_status'] for d in decisions)),
            review_status_counts=dict(Counter(r['review_status'] for r in reviews)),
            authoritative_action_calls=sum(c['role']=='ACTION' for c in calls),
            decision_commentary_calls=sum(c['role']=='COMMENTARY' for c in calls),
            self_review_calls=sum(c['role']=='SELF_REVIEW' for c in calls),
            transport_attempts=len(transport),
            invalid_action_outputs=sum(c['role']=='ACTION' and c['status']=='INVALID' for c in parsed),
            invalid_commentary_outputs=sum(c['role']=='COMMENTARY' and c['status']=='INVALID_DECISION_COMMENTARY' for c in parsed),
            invalid_review_outputs=sum(c['role']=='SELF_REVIEW' and c['status']=='INVALID_SELF_REVIEW' for c in parsed),
            grounded_memory_events=memory.checkpoint()['event_count'],grounded_memory_bytes=(path/'memory.sqlite3').stat().st_size)
        timeline=[f"{d['decision_id']} state={d['state']} action={d['selected_action']} "
            f"grounded={d['selected_grounded_before']['kind']} consequence={d['realized']['consequence']:+d} "
            f"next={d['realized']['next_state']} commentary={d['commentary_status']}" for d in decisions]
        review_summary=[dict(review_id=r['review_id'],after_decision=r['after_decision'],
            reviewed_decisions=r['reviewed_decisions'],review_status=r['review_status'],
            proposal_status=r['proposal_status'],SELF_REVIEW=r['SELF_REVIEW'],
            raw_model_output_sha256=r['raw_model_output_sha256'],
            no_memory_or_state_change=r['no_memory_or_state_change']) for r in reviews]
        return dict(behavioral_run_status='VALID',
            self_review_status='VALID' if metrics['invalid_review_outputs']==0 else 'PARTIAL_OR_INVALID',
            run=run,metrics=metrics,adaptation=adaptation,timeline=timeline,reviews=review_summary,
            decisions=decisions,restart='PASS' if run==RESTART_RUN else 'NOT_APPLICABLE',
            private_files_sha256={str(p.relative_to(path)):file_hash(p) for p in path.rglob('*') if p.is_file() and p.name!='.lock'})

def analyze(root):
    runs={run:analyze_run(root,run) for run in RUNS}
    result=dict(behavioral_campaign_status='VALID',
        self_analysis_status='SELF_ANALYSIS_NOT_ESTABLISHED' if all(
            r['metrics']['review_status_counts'].get('VALID_SELF_REVIEW',0)==0 for r in runs.values()) else
            'PENDING_PROPOSAL_AUDIT',runs=runs,
        interpretation='PENDING_INDEPENDENT_BEHAVIORAL_AND_PROPOSAL_AUDIT')
    _atomic_write(root/'analysis.json',result)
    return result

if __name__=='__main__':
    p=ArgumentParser();p.add_argument('--private-root',required=True,type=Path)
    x=analyze(p.parse_args().private_root)
    print(json.dumps({k:v for k,v in x.items() if k!='runs'}|{'runs':{r:v['metrics'] for r,v in x['runs'].items()}},indent=2,sort_keys=True))
