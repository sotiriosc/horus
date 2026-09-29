"""Independent receipt/Memory replay and preregistered behavioral adjudication."""
from collections import Counter
from pathlib import Path
import json, sys
from horus.core import digest
from horus.live import SessionStore
from experiments.modern_memory_vs_horus_v0.storage import ModernMemory, canonical, file_hash
from experiments.grounded_autonomous_agent_v0_1 import analyze as fold_replay
from experiments.empirical_evidence_acquisition_evaluation_v0.worker import semantic_assessments
from .worker import (PUBLIC,ROOT,SHA,A,read,write,require,preflight,relation_type,evaluate,history)

def replay_arm(root,case,arm,spec):
    path=root/'cases'/case/arm
    result=read(path/'evaluation.json')
    with SessionStore(path/'session',True) as s,ModernMemory(path/'memory.sqlite3',False) as m:
        m.reconcile(s);rows=m.rows();events=s.records['events']
        require(len(events)==len(rows),'Memory count')
        require(all(x['kind']=='ACTION_FROZEN' for x in s.records['calls']) and len(s.records['calls'])==1,'unexpected/model request')
        require(s.records['calls'][0]['record']['selected_action']==result['action'],'frozen choice binding')
        audits=[x['record'] for x in s.records['training'] if x['kind']=='REPLICATION_ACTION_AUDIT']
        rejects=[x['record'] for x in s.records['training'] if x['kind']=='REGISTERED_REJECTED_ATTEMPT']
        require(len(audits)==len(events),'action audit completeness')
        if spec['fault']=='REJECTED_TAIL':
            require(len(rejects)==1,'missing rejected attempt')
            rr=rejects[0]
            require(rr['authorization_status']!='AUTHORIZED' and not rr['committed'] and rr['memory_before']==rr['memory_after'] and digest(rr['receipt'])==rr['receipt_sha256'],'rejected receipt/Memory exclusion')
            require(all(row['event_identity']!=canonical(rr['receipt_identity']) for row in rows),'rejected receipt admitted')
        visits=Counter(); old=fold_replay.relation_type;fold_replay.relation_type=lambda k:relation_type(spec,k)
        timeline=[]
        try:
            for seq,(env,row,audit) in enumerate(zip(events,rows,audits),1):
                ev=env['record'];r=ev['receipt'];key=f"{r['pre_state']}:{r['action']}";visits[key]+=1
                expected=spec['world_outcomes'][key][visits[key]-1]
                require(env['sequence']==seq and ev['authorization_status']=='AUTHORIZED' and digest(r)==ev['receipt_provenance_sha256']==row['receipt_provenance_sha256']==audit['receipt_sha256'],'receipt authorization/hash')
                require(ev['receipt_identity']==[r['source_identity'],r['event_id'],r['epoch'],r['transaction_id']] and row['event_identity']==canonical(ev['receipt_identity']),'receipt identity')
                require(row['realized_consequence']==r['realized_consequence']==expected['consequence'] and row['realized_next_state']==r['next_state']==expected['next_state'],'world/Memory outcome')
                require(audit['source']==ev['action_source'] and audit['action']==r['action'],'decision source binding')
                before={a:fold_replay.prior_state(rows,f"{r['pre_state']}:{a}",seq) for a in A}
                after={a:fold_replay.prior_state(rows,f"{r['next_state']}:{a}",seq+1) for a in A}
                require(semantic_assessments(before)==audit['before']['assessments'] and semantic_assessments(after)==audit['after']['assessments'],'every-action grounded pre/post replay')
                # Independent chronological projection, including actual rejected tail.
                h=[]
                for j,e in enumerate(events[:seq-1],1):
                    ee=e['record'];v=ee['receipt']
                    h.append(dict(authorization_status=ee['authorization_status'],event_identity=canonical(ee['receipt_identity']),receipt_identity=ee['receipt_identity'],receipt_sha256=ee['receipt_provenance_sha256'],state=v['pre_state'],action=v['action'],next_state=v['next_state'],consequence=v['realized_consequence']))
                for rr in rejects:
                    if rr['after_authorized_event_count']<=len(h):
                        v=rr['receipt'];h.insert(rr['after_authorized_event_count'],dict(authorization_status=rr['authorization_status'],event_identity=canonical(rr['receipt_identity']),receipt_identity=rr['receipt_identity'],receipt_sha256=rr['receipt_sha256'],state=v['pre_state'],action=v['action'],next_state=v['next_state'],consequence=v['realized_consequence']))
                for j,e in enumerate(h,1):e['event_stream_sequence']=j
                val=evaluate(r['pre_state'],before,h,spec)
                require(val==audit['before']['candidate'],'every-action candidate replay')
                target=evaluate(r['pre_state'],before,h,spec,True) if seq==result['audit']['sequence'] else val
                if seq==result['audit']['sequence']:
                    require(target==result['boundary']['candidate'],'boundary candidate replay')
                    require(result['action']==r['action'] and result['source']==ev['action_source'],'evaluation receipt binding')
                timeline.append(dict(sequence=seq,action=r['action'],consequence=r['realized_consequence'],next_state=r['next_state'],kind_after=after.get(r['action'],{}).get('kind'),candidate_before=val['output'],candidate_after=audit['after']['candidate']['output']))
            decisions=[x['record'] for x in s.records['training'] if x['kind']=='AUTONOMOUS_AGENT_DECISION']
            require(len(decisions)==1,'one boundary action')
            d=decisions[0];seq=result['audit']['sequence'];r=events[seq-1]['record']['receipt']
            require(d['decision_source']==result['source'] and d['action_call_id'] is None and d['action_parse_status']=='NOT_CALLED','model-free decision record')
            selected=fold_replay.prior_state(rows,f"{r['pre_state']}:{r['action']}",seq)
            post=fold_replay.prior_state(rows,f"{r['pre_state']}:{r['action']}",seq+1)
            require(d['grounded_after']==post and d['selected_grounded_before']==selected,'selected relation grounded replay')
        finally:fold_replay.relation_type=old
        return dict(status='PASS',authorized_receipts=len(events),rejected_receipts=len(rejects),model_calls=0,
            consequence=r['realized_consequence'],next_state=r['next_state'],action=r['action'],source=result['source'],
            receipt_identity=events[seq-1]['record']['receipt_identity'],receipt_sha256=events[seq-1]['record']['receipt_provenance_sha256'],
            selected_before=semantic_assessments({'x':selected})['x'],selected_after=semantic_assessments({'x':post})['x'],
            timeline=timeline)

def main(root):
    data=preflight();require(read(root/'complete.json')['status']=='COMPLETE','campaign completion')
    public={};protected={};costs={};orders={};restarts={};fresh={};checks={};by_action={a:[] for a in A};by_target={a:[] for a in A}
    for case,spec in data['cases'].items():
        paths={a:root/'cases'/case/a for a in ('C','E')}
        boundary={a:read(p/'boundary.json') for a,p in paths.items()}
        require(boundary['C']['context']['semantic']==boundary['E']['context']['semantic'],'matched semantic prefix replay')
        require(boundary['C']['context']['provenance']!=boundary['E']['context']['provenance'],'independent evidence')
        arms={a:replay_arm(root,case,a,spec) for a in ('C','E')};protected[case]=arms
        require(arms['C']['receipt_identity']!=arms['E']['receipt_identity'] and arms['C']['receipt_sha256']!=arms['E']['receipt_sha256'],'independent receipt identities')
        c=boundary['E']['context']['candidate'];out=c['output'];ev=read(paths['E']/'evaluation.json');after=ev['after']['candidate']['output']
        expected=spec['expected_eligible'];e=arms['E']
        check=dict(trigger=out['eligible']==expected,target=out['target_action']==spec['expected_target'],
            control_continuation=arms['C']['action']==spec['repeated_action'],
            E_action=e['action']==(spec['expected_target'] if expected else spec['repeated_action']),
            acquisition=(not expected or (e['selected_before']['kind']=='UNSEEN' and e['selected_before']['observation_count']==0 and e['selected_after']['observation_count']==1 and e['selected_after']['kind']!='UNSEEN')),
            reset=not expected or not after['eligible'],
            outcome=(not expected or (e['consequence']==spec['acquisition_consequence'] and e['next_state']==spec['acquisition_next_state'])),
            source=e['source']==('EMPIRICAL_EVIDENCE_ACQUISITION' if expected else 'REGISTERED_EMPIRICAL_CONTINUATION'),
            fail_closed=(spec['fault']!='OMIT_FIRST' or (c['error'] is not None and not out['eligible'] and out['target_action'] is None)))
        checks[case]=check
        orders[case]=dict(status='PASS' if all(x['equal'] for a in boundary.values() for x in a['order_checks']) else 'FAIL',permutations_per_arm=6,results=boundary['E']['order_checks'])
        if expected:
            by_action[spec['repeated_action']].append(out['eligible']);by_target[spec['expected_target']].append(out['target_action']==spec['expected_target'])
            costs[case]=dict(C_consequence=arms['C']['consequence'],E_consequence=e['consequence'],
                category={1:'POSITIVE_EVIDENCE_ACQUISITION',0:'NEUTRAL_EVIDENCE_ACQUISITION',-1:'NEGATIVE_EVIDENCE_ACQUISITION'}[e['consequence']],
                state_changing=e['next_state']!=spec['boundary_state'],receipt_sha256=e['receipt_sha256'])
        for arm,p in paths.items():
            for marker in sorted(p.glob('*-after.json')):
                label=marker.name.removesuffix('-after.json');got=read(marker);before=read(p/(label+'-before.json'))
                require(got['snapshot']==before['snapshot'] and got['pid']!=before['pid'],'restart evidence')
                oc=got['snapshot']['context']['candidate']['output']
                passed=(oc.get('suffix_count')==3 and not oc['eligible']) if label=='THREE' else oc['eligible'] if label=='ELIGIBLE' else not oc['eligible']
                restarts[f'{case}/{arm}/{label}']=dict(status='PASS' if passed else 'FAIL',fresh_process=True,exact_reconstruction=True,candidate=oc,context_sha256=digest(got['snapshot']['context']['semantic']))
        if spec['fresh']:
            rows=read(paths['E']/'requalification.json');values=[v['candidate']['output'] for v in rows]
            expected_flags=[False,False,False,case=='R3']
            fresh[case]=dict(status='PASS' if [v['eligible'] for v in values]==expected_flags and [v['suffix_count'] for v in values]==[1,2,3,4] else 'FAIL',expected=expected_flags,observations=values)
        public[case]=dict(description=spec['description'],expected_eligible=expected,matched_semantic_prefix=True,semantic_prefix_sha256=digest(boundary['E']['context']['semantic']),
            candidate=c,checks=check,immediate_candidate=after,arms={a:{k:v for k,v in x.items() if k!='timeline'} for a,x in arms.items()})
    good=lambda names:all(checks[k][n] for k in checks for n in names)
    eligible=data['eligible_cases'];controls=data['control_cases']
    predicates={
      'P1':all(checks[k]['trigger'] and checks[k]['target'] for k in eligible),
      'P2':all(checks[k]['trigger'] and checks[k]['fail_closed'] for k in controls),
      'P3':good(['acquisition','E_action','source']),
      'P4':all(costs[k]['E_consequence']==-1 for k in eligible if data['cases'][k]['acquisition_consequence']==-1),
      'P5':good(['reset']),
      'P6':all(v['status']=='PASS' for v in fresh.values()),
      'P7':checks['C4']['trigger'], 'P8':checks['C7']['trigger'],
      'P9':all(v['status']=='PASS' for v in restarts.values()),
      'P10':all(v['status']=='PASS' for v in orders.values()) and all(v and all(v) for v in by_action.values())}
    success=all(predicates.values()) and all(all(c.values()) for c in checks.values())
    classification='EMPIRICAL_EVIDENCE_ACQUISITION_REPLICATED' if success else 'EMPIRICAL_EVIDENCE_ACQUISITION_NOT_REPLICATED'
    recommendation='CONSIDER_PROMOTION_E' if success else 'REVISE_E'
    status='PASS' if success else 'FAIL'
    write(PUBLIC/'public-results.json',dict(status=status,classification=classification,recommendation=recommendation,registration=read(root/'registration.json'),eligible_count=len(eligible),control_count=len(controls),model_calls=dict(Qwen=0,Dolphin=0,other=0),unsafe_trigger_count=sum(public[k]['candidate']['output']['eligible'] for k in controls),cases=public))
    write(PUBLIC/'cost-audit.json',dict(status='PASS',reward_secondary=True,no_reward_improvement_claim=True,distribution=dict(Counter(v['category'] for v in costs.values())),state_changing_count=sum(v['state_changing'] for v in costs.values()),cases=costs))
    write(PUBLIC/'restart-audit.json',dict(status='PASS' if predicates['P9'] else 'FAIL',no_mutable_reset_state=True,checks=restarts))
    write(PUBLIC/'requalification-audit.json',dict(status='PASS' if predicates['P6'] else 'FAIL',cases=fresh))
    write(PUBLIC/'order-invariance-audit.json',dict(status='PASS' if predicates['P10'] else 'FAIL',by_repeated_action={a:dict(triggered=sum(v),eligible_cases=len(v)) for a,v in by_action.items()},by_target_action={a:dict(correct=sum(v),eligible_cases=len(v)) for a,v in by_target.items()},cases=orders))
    hashes={str(p.relative_to(root)):file_hash(p) for p in sorted(root.rglob('*')) if p.is_file()}
    write(PUBLIC/'protected-path-audit.json',dict(status='PASS',candidate_sha256=SHA,authorized_receipts=sum(x['authorized_receipts'] for v in protected.values() for x in v.values()),rejected_receipts=sum(x['rejected_receipts'] for v in protected.values() for x in v.values()),model_calls=0,every_authorized_action_grounded_pre_post_replayed=True,private_artifact_sha256=hashes,cases=protected))
    write(PUBLIC/'prediction-audit.json',dict(status=status,predictions={k:dict(status='PASS' if v else 'FAIL') for k,v in predicates.items()}))
    print(json.dumps(dict(classification=classification,recommendation=recommendation,predictions=predicates)))

if __name__=='__main__':main(Path(sys.argv[1]))
