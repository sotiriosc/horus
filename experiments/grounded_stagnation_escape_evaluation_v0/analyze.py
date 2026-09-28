"""Read-only independent signed receipt, grounded replay, scope and outcome audit."""
from argparse import ArgumentParser
from collections import Counter
from pathlib import Path
import json
from horus.live import SessionStore,_atomic_write
from horus.core import digest
from experiments.modern_memory_vs_horus_v0.storage import ModernMemory,file_hash
from experiments.grounded_autonomous_agent_v0_1.analyze import prior_state
from experiments.grounded_autonomous_agent_v0_2.worker import rows_of
from experiments.grounded_authority_autonomous_agent_v0.protocol import ACTIONS,select_route,source_for_model_choice
from .candidate import THRESHOLD,SOURCE,PURPOSE
from .worker import CASES,ARMS

def qualifies(d):
    a=d['selected_action'];x=d['grounded_assessments_before'][a]
    return (d['decision_source']=='SAFE_GROUNDED_FALLBACK' and d['policy_route']=='MODEL' and
        d['action_parse_status']=='VALID' and x['relation_type']=='DETERMINISTIC' and
        x['kind']=='ESTABLISHED' and x['established_value']['consequence']==0 and
        any(b!=a and d['grounded_assessments_before'][b]['kind']=='UNSEEN' for b in ACTIONS) and
        all(not (v['relation_type']=='DETERMINISTIC' and v['kind']=='ESTABLISHED' and
            v['established_value']['consequence']==1)
            for v in d['grounded_assessments_before'].values()) and
        d['realized']==dict(next_state=d['state'],consequence=0))

def independent_suffix(history):
    count=0;relation=None
    for d in reversed(history):
        candidate=(d['state'],d['selected_action'])
        if not qualifies(d) or (relation is not None and candidate!=relation):break
        relation=candidate;count+=1
    return count,relation

def expected_escape(history,state,assessments):
    count,relation=independent_suffix(history)
    if count<THRESHOLD or relation is None or relation[0]!=state:return None,count
    fallback=relation[1];a=assessments[fallback]
    route=select_route(assessments)
    if (route['route']!='MODEL' or a['relation_type']!='DETERMINISTIC' or
        a['kind']!='ESTABLISHED' or a['established_value']['consequence']!=0 or
        any(v==1 for v in route['known_values'].values())):return None,count
    unseen=[b for b in ACTIONS if b!=fallback and assessments[b]['kind']=='UNSEEN']
    return (unseen[0] if unseen else None),count

def audit_arm(root,case,arm):
    path=root/'cases'/case/arm
    with SessionStore(path/'session',True) as store,ModernMemory(path/'memory.sqlite3',False) as memory:
        memory.reconcile(store);all_rows=memory.rows()
        decisions=rows_of(store,'AUTONOMOUS_AGENT_DECISION')
        if len(all_rows)!=len(store.records['events']):raise RuntimeError('event/Memory count mismatch')
        if rows_of(store,'SELF_REVIEW_NON_AUTHORITATIVE'):
            raise RuntimeError('self-review forbidden')
        frozen=[x['record'] for x in store.records['calls'] if x['kind']=='ACTION_FROZEN']
        if len(frozen)!=len(decisions):raise RuntimeError('action freeze count mismatch')
        for j,(d,f) in enumerate(zip(decisions,frozen)):
            seq=d['event_stream_sequence'];envelope=store.records['events'][seq-1]
            e=envelope['record'];r=e['receipt'];a=d['selected_action'];state=d['state']
            if (d['index']!=j+1 or d['decision_id']!=f'C:D{j+1:02d}' or
                a not in ACTIONS or e['authorization_status']!='AUTHORIZED' or
                e['decision_index']!=d['index'] or r['pre_state']!=state or r['action']!=a or
                d['receipt_identity']!=e['receipt_identity'] or
                d['receipt_provenance_sha256']!=e['receipt_provenance_sha256'] or
                digest(r)!=e['receipt_provenance_sha256'] or
                d['realized']!=dict(next_state=r['next_state'],consequence=r['realized_consequence'])):
                raise RuntimeError('signed decision/receipt mismatch')
            for b in ACTIONS:
                if d['grounded_assessments_before'][b]!=prior_state(all_rows,f'{state}:{b}',seq):
                    raise RuntimeError('grounded predecision replay mismatch')
            if d['grounded_after']!=prior_state(all_rows,f'{state}:{a}',seq+1):
                raise RuntimeError('grounded postreceipt replay mismatch')
            if (f['selected_action']!=a or f['decision_source']!=d['decision_source'] or
                f['action_call_id']!=d['action_call_id']):
                raise RuntimeError('frozen action mismatch')
            base=select_route(d['grounded_assessments_before'])
            if d['admissible_actions']!=base['candidates'] or a not in base['candidates']:
                raise RuntimeError('incumbent candidate set mismatch')
            expected,count=expected_escape(decisions[:j],state,d['grounded_assessments_before'])
            if d['counter_before']!=count:raise RuntimeError('counter reconstruction mismatch')
            if d['decision_source']==SOURCE:
                if (arm!='S' or expected!=a or d['policy_route']!='ESCAPE' or
                    d['policy_reason']!=PURPOSE or d['acquisition_purpose']!=PURPOSE or
                    d['action_call_id'] is not None or d['action_parse_status']!='NOT_CALLED' or
                    d['selected_grounded_before']['kind']!='UNSEEN'):
                    raise RuntimeError('FALSE_TRIGGER')
            else:
                if arm=='S' and expected is not None:
                    raise RuntimeError('eligible S trigger omitted')
                source=(base['source'] if base['route']=='MECHANICAL' else
                        source_for_model_choice(base,d['grounded_assessments_before'],a))
                if (d['decision_source']!=source or d['policy_route']!=base['route'] or
                    d['policy_reason']!=base['reason'] or
                    (base['route']=='MODEL')!=(d['action_call_id'] is not None)):
                    raise RuntimeError('incumbent route changed')
                if base['route']=='MODEL' and d['action_parse_status']!='VALID':
                    raise RuntimeError('invalid action executed')
                if base['route']=='MECHANICAL' and (a!=base['action'] or
                    d['action_parse_status']!='NOT_CALLED'):
                    raise RuntimeError('mechanical ceiling displaced')
        intents=[x['record'] for x in store.records['calls'] if x['kind']=='REQUEST_INTENT']
        if any(x['role']!='ACTION' for x in intents):raise RuntimeError('non-action model call')
        if len(intents)!=sum(d['action_call_id'] is not None for d in decisions):
            raise RuntimeError('action model call count mismatch')
        if case=='H':
            verdict=json.loads((path/'restart-verdict.json').read_text())
            if verdict['status']!='PASS' or verdict['suffix']['count']!=2:
                raise RuntimeError('restart suffix mismatch')
        streaks=[];current=0;relation=None
        for d in decisions:
            key=(d['state'],d['selected_action'])
            current=current+1 if qualifies(d) and (relation is None or key==relation) else 1 if qualifies(d) else 0
            relation=key if current else None;streaks.append(current)
        escapes=[]
        for d in decisions:
            if d['decision_source']!=SOURCE:continue
            relation=f"{d['state']}:{d['selected_action']}"
            later=[x for x in decisions if x['index']>d['index']]
            escape=dict(decision_id=d['decision_id'],relation=relation,
                first_receipt_identity=d['receipt_identity'],
                receipt_provenance_sha256=d['receipt_provenance_sha256'],
                grounded_after_kind=d['grounded_after']['kind'],
                realized=d['realized'],
                acquisition_class=('NEGATIVE_ACQUISITION_COST' if d['realized']['consequence']<0 else
                    'POSITIVE_ACQUISITION_OUTCOME' if d['realized']['consequence']>0 else
                    'NEUTRAL_ACQUISITION'),
                revisited=any(x['state']==d['state'] and x['selected_action']==d['selected_action'] for x in later),
                later_selected_with_grounded_evidence=[x['decision_id'] for x in later
                    if x['state']==d['state'] and x['selected_action']==d['selected_action'] and
                    x['selected_grounded_before']['kind']!='UNSEEN'],
                later_uncertainty=[dict(decision_id=x['decision_id'],kind=x['selected_grounded_before']['kind'])
                    for x in later if x['state']==d['state'] and x['selected_action']==d['selected_action'] and
                    x['selected_grounded_before']['kind'] in ('UNRESOLVED_CHANGE','POSSIBLE_REGIME_CHANGE','VARIABLE_RELATION')],
                downstream_realized_consequence=sum(x['realized']['consequence'] for x in later))
            escapes.append(escape)
        setup=[e['record'] for e in store.records['events'] if e['record']['execution_kind']=='REGISTERED_SETUP']
        result=dict(case=case,arm=arm,decisions=decisions,escapes=escapes,
            metrics=dict(decisions=len(decisions),setup_events=len(setup),
                total_realized_consequence=sum(d['realized']['consequence'] for d in decisions),
                prefix_realized_consequence=sum(d['realized']['consequence'] for d in decisions if d['index']<=7) if case in 'ABCDH' else 0,
                postfork_realized_consequence=sum(d['realized']['consequence'] for d in decisions if d['index']>=8) if case in 'ABCD' else sum(d['realized']['consequence'] for d in decisions if d['index']>=7) if case=='H' else sum(d['realized']['consequence'] for d in decisions),
                maximum_qualifying_streak=max(streaks,default=0),
                model_action_calls=len(intents),mechanical_decisions=sum(d['action_call_id'] is None for d in decisions),
                calls_avoided_by_escape=len(escapes),
                context_tokens=sum(d['action_context_tokens'] for d in decisions),
                output_tokens=sum(d['action_output_tokens'] for d in decisions),
                inference_latency_seconds=sum(d['action_model_latency_seconds'] for d in decisions),
                trigger_count=len(escapes),false_trigger_count=0),
            private_files_sha256={str(p.relative_to(path)):file_hash(p) for p in path.rglob('*')
                if p.is_file() and p.name!='.lock'})
        return result

def audit_matched_prefix(root,case):
    """Check signed bytes of every common observation/decision before fork."""
    paths=[root/'cases'/case/arm for arm in ARMS]
    opened=[]
    try:
        for path in paths:
            store=SessionStore(path/'session',True)
            memory=ModernMemory(path/'memory.sqlite3',False)
            memory.reconcile(store)
            opened.append((store,memory))
        (i,im),(s,sm)=opened
        n=7 if case in 'ABCDH' else 1 if case in 'EG' else 3
        training=7 if case in 'ABCDH' else 0
        if i.records['events'][:n]!=s.records['events'][:n]:
            raise RuntimeError('matched signed event prefix differs')
        if i.records['training'][:training]!=s.records['training'][:training]:
            raise RuntimeError('matched signed decision prefix differs')
        if im.rows()[:n]!=sm.rows()[:n]:
            raise RuntimeError('matched grounded Memory prefix differs')
        if training:
            def call_prefix(store):
                calls=[]
                for envelope in store.records['calls']:
                    calls.append(envelope)
                    if envelope['kind']=='ACTION_FROZEN' and envelope['record']['decision_id']=='C:D07':
                        return calls
                raise RuntimeError('matched D07 call freeze missing')
            if call_prefix(i)!=call_prefix(s):
                raise RuntimeError('matched model request/call prefix differs')
        return dict(status='PASS',shared_authorized_events=n,
            shared_decisions=training,predivergence_model_inputs_identical=True)
    finally:
        for store,memory in opened:
            memory.close();store.close()

def analyze(root):
    matched_prefix={case:audit_matched_prefix(root,case) for case in CASES}
    runs={case:{arm:audit_arm(root,case,arm) for arm in ARMS} for case in CASES}
    paired={};relative=0;eligible=0
    for case,arms in runs.items():
        I=arms['I'];S=arms['S'];comparisons=[]
        for escape in S['escapes']:
            matching=next((d for d in I['decisions'] if d['index']==int(escape['decision_id'].split('D')[1])),None)
            if matching is None:raise RuntimeError('missing matched incumbent decision')
            relation=escape['relation'];state,action=relation.split(':')
            still_unseen=(matching['state']==int(state) and
                matching['grounded_assessments_before'][action]['kind']=='UNSEEN' and
                matching['selected_action']!=action)
            comparisons.append(dict(escape_decision=escape['decision_id'],relation=relation,
                incumbent_selected=matching['selected_action'],
                I_relation_remained_unseen_after_matched_decision=still_unseen))
        paired[case]=comparisons
        if case in 'ABCD':
            eligible+=bool(S['escapes'])
            relative+=any(x['I_relation_remained_unseen_after_matched_decision'] for x in comparisons)
    if relative<2 or eligible<2:classification='H1_NOT_SUPPORTED'
    elif (all(runs[c]['S']['metrics']['postfork_realized_consequence']<
              runs[c]['I']['metrics']['postfork_realized_consequence'] for c in 'ABCD' if runs[c]['S']['escapes'])
          and all(not e['later_selected_with_grounded_evidence'] for c in 'ABCD'
                  for e in runs[c]['S']['escapes'])):
        classification='COST_DOMINATES_REGISTERED_USE'
    else:classification='STAGNATION_ESCAPE_SUPPORTED'
    result=dict(campaign_status='VALID',classification=classification,
        eligible_ABCD_cases=eligible,relative_acquisition_ABCD_cases=relative,
        paired_primary=paired,matched_prefix=matched_prefix,runs=runs,
        promotion_recommendation='DO_NOT_PROMOTE_AUTOMATICALLY')
    _atomic_write(root/'analysis.private.json',result)
    return result

if __name__=='__main__':
    p=ArgumentParser();p.add_argument('--private-root',required=True,type=Path)
    x=analyze(p.parse_args().private_root)
    print(json.dumps({k:v for k,v in x.items() if k!='runs'},indent=2,sort_keys=True))
