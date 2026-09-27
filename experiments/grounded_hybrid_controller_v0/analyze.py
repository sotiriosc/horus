"""Separate autonomous, epistemic, and operational measurements."""
from argparse import ArgumentParser
import json
from pathlib import Path
from horus.live import SessionStore,RegimeEpisodeWorld
from .protocol import ARMS,SCENARIOS,MAX_DECISIONS,MODEL_LOGICAL_CEILING,TOTAL_LOGICAL_CEILING

def _decisions(output,scenario,arm):
    with SessionStore(output/'scenarios'/scenario/'work'/arm/'session',True) as store:
        decisions=[e['record'] for e in store.records['training'] if e['kind']=='HYBRID_CONTROLLER_DECISION']
        calls=store.records['calls']
        return decisions,calls

def _counterfactual(decision,regime):
    results={}
    for action in decision['candidate_actions']:
        world=RegimeEpisodeWorld(decision['pre_state'],regime)
        results[action]=world.execute(1,1,action).consequence
    return results

def analyze(output):
    rows={name:{arm:_decisions(output,name,arm)[0] for arm in ARMS} for name in SCENARIOS}
    complete=(output/'campaign-complete.json').exists() and all(
        len(rows[name][arm])==(2 if SCENARIOS[name].get('second_decision') else 1)
        for name in SCENARIOS for arm in ARMS)
    totals={};costs={};per_scenario={};epistemic=dict(GROUNDED_WHEN_JUSTIFIED=0,
        MODEL_ONLY_WHEN_UNSEEN=0,UNRESOLVED_WHEN_EVIDENCE_INSUFFICIENT=0,
        FALSE_CERTAINTY=0,MISSED_KNOWN_VALUE=0)
    for arm in ARMS:
        data=[d for name in SCENARIOS for d in rows[name][arm]]
        chosen=[d for d in data if d['selected_action'] is not None]
        incorrect=0;source_counts={};blocked=0;unnecessary=0
        for name in SCENARIOS:
            for d in rows[name][arm]:
                if d['selected_action'] is None:
                    if arm=='HYBRID':
                        blocked+=d['reason']=='ABSTAIN_UNRESOLVED_COULD_CHANGE_WINNER'
                        counter=_counterfactual(d,SCENARIOS[name]['regime'])
                        unnecessary+=len([v for v in counter.values() if v==max(counter.values())])==1
                    continue
                a=next(a for a in d['assessments'] if a['action']==d['selected_action'])
                source_counts[a['status']]=source_counts.get(a['status'],0)+1
                incorrect+=a['value']['consequence']!=d['realized']['consequence']
        totals[arm]=dict(decisions=len(data),executed=len(chosen),abstentions=len(data)-len(chosen),
            realized_consequence_sum=sum(d['realized']['consequence'] for d in chosen),
            realized_consequences=[dict(scenario=d['scenario'],index=d['index'],
                action=d['selected_action'],consequence=d['realized']['consequence']) for d in chosen],
            incorrect_confident_actions=incorrect,selected_source_counts=source_counts,
            decisions_blocked_by_unresolved=blocked,retrospectively_unnecessary_abstentions=unnecessary)
        allcalls=[]
        for name in SCENARIOS:
            _,calls=_decisions(output,name,arm);allcalls.extend(calls)
        logical=sum(e['kind']=='REQUEST_INTENT' for e in allcalls)
        physical=sum(e['kind']=='TRANSPORT_ATTEMPT_INTENT' for e in allcalls)
        costs[arm]=dict(logical_model_calls=logical,physical_model_attempts=physical,
            context_tokens=sum(d['context_tokens'] for d in data),
            mechanical_derivation_seconds=sum(d['mechanical_seconds'] for d in data),
            decision_seconds=sum(d['decision_seconds'] for d in data),
            model_calls_recorded_in_decisions=sum(d['model_calls'] for d in data),
            mean_serialized_grounded_state_bytes=(sum(a['serialized_grounded_state_bytes']
                for d in data for a in d['assessments'])/sum(len(d['assessments']) for d in data)),
            max_serialized_grounded_state_bytes=max(a['serialized_grounded_state_bytes']
                for d in data for a in d['assessments']))
    for name in SCENARIOS:
        per_scenario[name]={arm:[dict(index=d['index'],action=d['selected_action'],
            reason=d['reason'],realized_consequence=(None if d['realized'] is None else d['realized']['consequence']),
            selected_status=(None if d['selected_action'] is None else next(a['status']
                for a in d['assessments'] if a['action']==d['selected_action'])),
            model_calls=d['model_calls']) for d in rows[name][arm]] for arm in ARMS}
    for name in SCENARIOS:
        for d in rows[name]['HYBRID']:
            for a in d['assessments']:
                kind=a['grounded_state_kind'];status=a['status']
                if kind=='ESTABLISHED':
                    if status=='GROUNDED' and a['model_calls']==0 and a['value']==a['established_value'] and a['established_support']:
                        epistemic['GROUNDED_WHEN_JUSTIFIED']+=1
                    else:epistemic['MISSED_KNOWN_VALUE']+=1
                elif kind=='UNSEEN':
                    if status=='MODEL_GENERALIZATION' and a['model_calls']==2 and not a['provenance']:
                        epistemic['MODEL_ONLY_WHEN_UNSEEN']+=1
                    else:epistemic['FALSE_CERTAINTY']+=1
                elif kind=='UNRESOLVED_CHANGE':
                    if status=='UNRESOLVED' and a['value'] is None and a['model_calls']==0 and a['candidate_support']:
                        epistemic['UNRESOLVED_WHEN_EVIDENCE_INSUFFICIENT']+=1
                    else:epistemic['FALSE_CERTAINTY']+=1
                else:epistemic['FALSE_CERTAINTY']+=1
    e=rows['E_MULTIPLE_UNSEEN']['HYBRID'];selected=e[0]['selected_action']
    e_handoff=(selected is not None and next(a for a in e[0]['assessments'] if a['action']==selected)['status']=='MODEL_GENERALIZATION'
        and next(a for a in e[1]['assessments'] if a['action']==selected)['status']=='GROUNDED')
    hroot=output/'scenarios/H_RESTART_UNRESOLVED'
    restart=json.loads((hroot/'restart.json').read_text()) if complete else None
    perturb=json.loads((hroot/'perturbation.json').read_text()) if complete else None
    targets=('A_ALL_ESTABLISHED','B_ESTABLISHED_UNSEEN','C_ESTABLISHED_UNRESOLVED',
             'E_MULTIPLE_UNSEEN','F_CANDIDATE_CONFIRMED','G_RESTORATION','I_ANOMALY_REJECTED')
    useful=all(rows[name]['HYBRID'][0]['selected_action'] is not None and
        rows[name]['HYBRID'][0]['realized']['consequence']>=0 for name in targets)
    abstain=all(rows[name]['HYBRID'][0]['selected_action'] is None for name in
        ('D_UNRESOLVED_BEST','H_RESTART_UNRESOLVED'))
    integrity=bool(complete and restart and restart['status']=='PASS' and perturb and perturb['status']=='PASS'
        and epistemic['FALSE_CERTAINTY']==0 and epistemic['MISSED_KNOWN_VALUE']==0
        and costs['HYBRID']['logical_model_calls']==costs['HYBRID']['model_calls_recorded_in_decisions']
        and costs['MODEL']['logical_model_calls']==costs['MODEL']['model_calls_recorded_in_decisions']
        and costs['FORCED_GROUNDED']['logical_model_calls']==0
        and costs['MODEL']['logical_model_calls']==MODEL_LOGICAL_CEILING
        and sum(costs[a]['logical_model_calls'] for a in ARMS)<=TOTAL_LOGICAL_CEILING)
    matched=[(rows[name]['HYBRID'][0],rows[name]['MODEL'][0]) for name in SCENARIOS
        if rows[name]['HYBRID'][0]['realized'] is not None and rows[name]['MODEL'][0]['realized'] is not None]
    model_wins=sum(m['realized']['consequence']>h['realized']['consequence'] for h,m in matched)
    hybrid_wins=sum(h['realized']['consequence']>m['realized']['consequence'] for h,m in matched)
    model_advantage=sum(m['realized']['consequence']-h['realized']['consequence'] for h,m in matched)
    model_superior=model_wins>=3 and hybrid_wins==0 and model_advantage>=3
    forced_same=all(rows[name]['HYBRID'][0]['selected_action']==rows[name]['FORCED_GROUNDED'][0]['selected_action']
        for name in SCENARIOS)
    if not integrity:classification='INVALID'
    elif model_superior:classification='MODEL_DEFAULT_SUPERIOR'
    elif forced_same:classification='FORCED_POINT_SUFFICIENT'
    elif useful and abstain and e_handoff:classification='GROUNDED_HYBRID_SUPPORTED'
    else:classification='MIXED'
    boundary=dict(shared_prefix=('RETREAT:+0,ADVANCE:+1,HOLD:+1,HOLD:-1'),
        next_confirmed_value=-1,next_rejected_value=1,
        status='EVIDENCE_INSUFFICIENT_TO_DISTINGUISH' if complete else 'NOT_EVALUATED')
    result=dict(status='COMPLETE' if complete else 'STOPPED',classification=classification,
        scenarios=list(SCENARIOS),arms=list(ARMS),decisions_per_arm=MAX_DECISIONS,
        totals=totals,operational=costs,per_scenario=per_scenario,
        epistemic=epistemic,model_to_grounded_handoff=e_handoff,
        information_boundary=boundary,
        model_calls_avoided_vs_model=costs['MODEL']['logical_model_calls']-costs['HYBRID']['logical_model_calls'],
        hybrid_model_calls_required_for_unseen=costs['HYBRID']['logical_model_calls'],
        hybrid_calls_avoided_for_established=2*epistemic['GROUNDED_WHEN_JUSTIFIED'],
        hybrid_calls_avoided_for_unresolved=2*epistemic['UNRESOLVED_WHEN_EVIDENCE_INSUFFICIENT'],
        restart=restart,perturbation=perturb,
        limitations=['Small deterministic world with two registered hidden regimes; no population inference.',
            'Seed observations are controlled; only decision-stage actions are autonomous.',
            'Second E decisions follow arm-specific autonomous histories and are descriptive, not matched.',
            'Retrospective unnecessary abstentions use analysis-only registered-world counterfactuals, not authenticated receipts.',
            'Grounded evidence is historical; a hidden regime can change before the next receipt.',
            'The +1 selector uses the registered global consequence bound; a different world requires a new bound.'])
    (output/'results.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    return result
if __name__=='__main__':
    p=ArgumentParser();p.add_argument('--output',type=Path,required=True)
    print(json.dumps(analyze(p.parse_args().output),sort_keys=True))
