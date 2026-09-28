"""Independent signed replay and preregistered replication/promotion audit."""
from argparse import ArgumentParser
from pathlib import Path
import json
from horus.live import SessionStore,_atomic_write
from experiments.modern_memory_vs_horus_v0.storage import ModernMemory,file_hash
from experiments.grounded_stagnation_escape_evaluation_v0.analyze import audit_arm
from .worker import ELIGIBLE,CONTROLS,GROUPS,CONTROL_SETUP

ARMS=('I','S')
CASES=ELIGIBLE+CONTROLS+('RA','RB')
GROUP_OF={case:group for group,spec in GROUPS.items() for case in spec['cases']}

def signed_prefix(root,case):
    """Compare actual signed common records, not reconstructed semantic values."""
    paths=[root/'cases'/case/arm for arm in ARMS]
    opened=[]
    try:
        for path in paths:
            store=SessionStore(path/'session',True)
            memory=ModernMemory(path/'memory.sqlite3',False)
            memory.reconcile(store);opened.append((store,memory))
        (i,im),(s,sm)=opened
        setup=(len(GROUPS[GROUP_OF[case]]['setup']) if case in GROUP_OF else
               len(CONTROL_SETUP[case]['actions']) if case in CONTROL_SETUP else 1)
        decisions=3 if case in ELIGIBLE+('RA',) else 0
        n=setup+decisions
        if i.records['events'][:n]!=s.records['events'][:n]:
            raise RuntimeError('matched signed event prefix differs')
        if i.records['training'][:decisions]!=s.records['training'][:decisions]:
            raise RuntimeError('matched signed decision prefix differs')
        if im.rows()[:n]!=sm.rows()[:n]:
            raise RuntimeError('matched Memory prefix differs')
        if decisions:
            def calls_through_d3(store):
                rows=[]
                for row in store.records['calls']:
                    rows.append(row)
                    if row['kind']=='ACTION_FROZEN' and row['record']['decision_id']=='C:D03':
                        return rows
                raise RuntimeError('missing common D03 action freeze')
            if calls_through_d3(i)!=calls_through_d3(s):
                raise RuntimeError('matched model request/call prefix differs')
        return dict(status='PASS',shared_authorized_events=n,
            shared_decisions=decisions,predivergence_model_inputs_identical=True)
    finally:
        for store,memory in opened:
            memory.close();store.close()

def rb_prefix(root):
    paths=[root/'cases'/'R4'/'S',root/'cases'/'RB'/'S']
    opened=[]
    try:
        for path in paths:
            s=SessionStore(path/'session',True);m=ModernMemory(path/'memory.sqlite3',False)
            m.reconcile(s);opened.append((s,m))
        (a,am),(b,bm)=opened
        if a.records['events'][:5]!=b.records['events'][:5] or \
           a.records['training'][:4]!=b.records['training'][:4] or \
           am.rows()[:5]!=bm.rows()[:5]:
            raise RuntimeError('RB not copied after R4 S D04')
        return dict(status='PASS',shared_authorized_events=5,shared_decisions=4)
    finally:
        for s,m in opened:m.close();s.close()

def matched_escape(I,S):
    comparisons=[]
    for escape in S['escapes']:
        index=int(escape['decision_id'].split('D')[1])
        d=next((x for x in I['decisions'] if x['index']==index),None)
        if d is None:raise RuntimeError('missing matched I decision')
        state,action=escape['relation'].split(':')
        primary=(d['state']==int(state) and
            d['grounded_assessments_before'][action]['kind']=='UNSEEN' and
            d['selected_action']!=action)
        later_exact=next((x['index'] for x in I['decisions'] if x['index']>index and
            x['state']==int(state) and x['selected_action']==action and
            x['selected_grounded_before']['kind']=='UNSEEN'),None)
        comparisons.append(dict(escape_decision=escape['decision_id'],relation=escape['relation'],
            matched_incumbent_action=d['selected_action'],
            I_relation_remained_unseen_after_matched_decision=primary,
            I_later_first_sampled_same_relation_at=later_exact))
    return comparisons

def first_new_after_fork(run):
    return next((d for d in run['decisions'] if d['index']>=4 and
        d['selected_grounded_before']['kind']=='UNSEEN'),None)

def audit(root):
    paired_prefix={case:signed_prefix(root,case) for case in ELIGIBLE+CONTROLS+('RA',)}
    paired_prefix['RB']=rb_prefix(root)
    runs={case:{arm:audit_arm(root,case,arm) for arm in ARMS} for case in ELIGIBLE+CONTROLS+('RA',)}
    runs['RB']={'S':audit_arm(root,'RB','S')}
    restart={}
    for case in ('RA','RB'):
        path=root/'cases'/case/'S'/'restart-verdict.json'
        verdict=json.loads(path.read_text())
        if not verdict['reconstructed_from_signed_history'] or not verdict['no_persisted_counter']:
            raise RuntimeError('restart reconstruction authority breach')
        expected=(verdict['observed_suffix']['count']==2 if case=='RA' else
                  verdict['prior_escape'] and verdict['observed_suffix']['count']==0)
        if (verdict['status']=='PASS')!=bool(expected):
            raise RuntimeError('restart verdict inconsistent with signed suffix')
        restart[case]=verdict
    paired={case:matched_escape(arms['I'],arms['S'])
            for case,arms in runs.items() if 'I' in arms}
    relative=[case for case in ELIGIBLE if any(
        x['I_relation_remained_unseen_after_matched_decision'] for x in paired[case])]
    escapes=[(case,e) for case in ELIGIBLE for e in runs[case]['S']['escapes']]
    triggered_states=sorted({int(e['relation'].split(':')[0]) for _,e in escapes})
    acquired_relations=sorted({e['relation'] for _,e in escapes})
    fallback_actions=sorted({runs[case]['S']['decisions'][2]['selected_action']
        for case,e in escapes if len(runs[case]['S']['decisions'])>=3})
    false_triggers=sum(arm['metrics']['false_trigger_count']
        for arms in runs.values() for arm in arms.values())
    if false_triggers or any(runs[c]['S']['escapes'] for c in CONTROLS):
        raise RuntimeError('FALSE_TRIGGER')
    r6_i=first_new_after_fork(runs['R6']['I'])
    r6_s=first_new_after_fork(runs['R6']['S'])
    r6_latency=dict(I_decision=None if r6_i is None else r6_i['index'],
        I_relation=None if r6_i is None else f"{r6_i['state']}:{r6_i['selected_action']}",
        S_decision=None if r6_s is None else r6_s['index'],
        S_relation=None if r6_s is None else f"{r6_s['state']}:{r6_s['selected_action']}",
        difference_decisions=None if r6_i is None or r6_s is None else r6_i['index']-r6_s['index'])
    useful_use=any(
        d['index']>int(e['decision_id'].split('D')[1]) and
        f"{d['state']}:{d['selected_action']}"==e['relation'] and
        d['decision_source']=='GROUNDED_MECHANICAL'
        for e in runs['R4']['S']['escapes'] for d in runs['R4']['S']['decisions'])
    control_action_mismatch=[case for case in CONTROLS if
        [d['selected_action'] for d in runs[case]['I']['decisions']]!=
        [d['selected_action'] for d in runs[case]['S']['decisions']]]
    major_unexpected_failure=[]
    for case,e in escapes:
        if e['acquisition_class']!='NEGATIVE_ACQUISITION_COST':continue
        idx=int(e['decision_id'].split('D')[1]);state,action=e['relation'].split(':')
        for d in runs[case]['S']['decisions']:
            if d['index']<=idx or d['state']!=int(state) or d['selected_action']!=action:continue
            known=d['known_values_before']
            if known.get(action) is not None and known[action]<0 and any(
                    v is not None and v>known[action] for a,v in known.items() if a!=action):
                major_unexpected_failure.append(dict(case=case,decision_id=d['decision_id']))
    negative_cost_block=False
    for case,e in escapes:
        if e['acquisition_class']!='NEGATIVE_ACQUISITION_COST':continue
        index=int(e['decision_id'].split('D')[1])
        S_down=sum(d['realized']['consequence'] for d in runs[case]['S']['decisions'] if d['index']>index)
        I_down=sum(d['realized']['consequence'] for d in runs[case]['I']['decisions'] if d['index']>index)
        if S_down<I_down:negative_cost_block=True
    core=(len(relative)>=4 and len(triggered_states)>=2 and len(fallback_actions)>=2 and
          len(acquired_relations)>=3)
    if not core:classification='STAGNATION_ESCAPE_NOT_GENERAL'
    elif negative_cost_block or control_action_mismatch or major_unexpected_failure:
        classification='COST_OR_SCOPE_BLOCKS_PROMOTION'
    elif r6_i is None or not useful_use or any(v['status']!='PASS' for v in restart.values()):
        classification='MORE_EVIDENCE_REQUIRED'
    else:classification='STAGNATION_ESCAPE_REPLICATED'
    recommendation=('PROMOTE_S' if classification=='STAGNATION_ESCAPE_REPLICATED' else
                    'RETAIN_INCUMBENT' if classification in ('STAGNATION_ESCAPE_NOT_GENERAL',
                        'COST_OR_SCOPE_BLOCKS_PROMOTION') else 'MORE_EVIDENCE_REQUIRED')
    result=dict(campaign_status='VALID',classification=classification,
        promotion_recommendation=recommendation,
        relative_acquisition_cases=relative,triggered_states=triggered_states,
        fallback_actions=fallback_actions,acquired_relations=acquired_relations,
        acquisition_outcome_counts={label:sum(e['acquisition_class']==label for _,e in escapes)
            for label in ('NEGATIVE_ACQUISITION_COST','NEUTRAL_ACQUISITION','POSITIVE_ACQUISITION_OUTCOME')},
        r6_any_new_relation_latency=r6_latency,R4_observed_later_use=useful_use,
        negative_downstream_cost_block=negative_cost_block,control_action_mismatch=control_action_mismatch,
        major_unexpected_failure=major_unexpected_failure,false_triggers=false_triggers,
        matched_prefix=paired_prefix,restart=restart,paired_primary=paired,runs=runs)
    _atomic_write(root/'analysis.private.json',result)
    return result

if __name__=='__main__':
    p=ArgumentParser();p.add_argument('--private-root',required=True,type=Path)
    x=audit(p.parse_args().private_root)
    print(json.dumps({k:v for k,v in x.items() if k!='runs'},sort_keys=True,indent=2))
