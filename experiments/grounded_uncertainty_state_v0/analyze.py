"""Prospectively defined receipt-grounded scoring and information-boundary audit."""
from argparse import ArgumentParser
from collections import Counter
import json
from pathlib import Path
from statistics import mean
from horus.live import SessionStore
from experiments.modern_memory_vs_horus_v0.storage import ModernMemory
from .protocol import ARMS,SCHEDULES,EVENTS_PER_ARM,MODEL_LOGICAL_CEILING,MODEL_PHYSICAL_CEILING
from .uncertainty import fold

def _rows(output,name,arm):
    with SessionStore(output/'schedules'/name/arm/'session',True) as store:
        return [e['record'] for e in store.records['training'] if e['kind']=='GROUNDED_UNCERTAINTY_SCORED_EVENT']

def _signature(rows,through):
    return tuple((r['state'],r['action'],r['realized']['next_state'],r['realized']['consequence'])
                 for r in rows[:through])

def analyze(output):
    allrows={name:{arm:_rows(output,name,arm) for arm in ARMS} for name in SCHEDULES}
    complete=(output/'campaign-complete.json').exists() and all(
        len(allrows[name][arm])==len(specs) for name,specs in SCHEDULES.items() for arm in ARMS)
    totals={};costs={};cold={};unresolved=[];transitions=[];prefix_audit=[];provenance=True
    for arm in ARMS:
        data=[r for name in SCHEDULES for r in allrows[name][arm]]
        totals[arm]=dict(events=len(data),point_consequence_correct=sum(r['consequence_correct'] for r in data),
            point_exact_correct=sum(r['exact_correct'] for r in data))
        costs[arm]=dict(logical_model_calls=sum(r['model_calls'] for r in data),
            context_tokens=sum(r['context_tokens'] for r in data),
            preparation_seconds=sum(r['model_seconds'] for r in data),
            mechanical_update_seconds=sum(r['mechanical_update_seconds'] for r in data),
            mean_state_bytes=mean(r['serialized_state_bytes'] for r in data) if data else 0)
        cold[arm]=dict(events=sum(not r['raw_eligible_memories'] for r in data),
            correct=sum(r['consequence_correct'] for r in data if not r['raw_eligible_memories']))
    u=[r for name in SCHEDULES for r in allrows[name]['U']]
    established=[r for r in u if r['grounded_state_before']['kind']=='ESTABLISHED']
    unresolved_pre=[r for r in u if r['grounded_state_before']['kind']=='UNRESOLVED_CHANGE']
    missed=0;post_established=0;post_unresolved=0
    for name in SCHEDULES:
        rows=allrows[name]['U']
        for i,row in enumerate(rows):
            before=row['grounded_state_before'];after=row['grounded_state_after']
            if after['kind']=='ESTABLISHED':post_established+=1
            if after['kind']=='UNRESOLVED_CHANGE':
                post_unresolved+=1
                peers=[]
                here=_signature(rows,i+1)
                for other,arms in allrows.items():
                    if other==name:continue
                    otherrows=arms['U']
                    if len(otherrows)>i+1 and _signature(otherrows,i+1)==here:
                        peers.append(dict(schedule=other,next_value=otherrows[i+1]['realized']))
                future=rows[i+1]['realized'] if i+1<len(rows) else None
                distinct={json.dumps(x,sort_keys=True) for x in [future]+[p['next_value'] for p in peers] if x is not None}
                boundary=('EVIDENCE_INSUFFICIENT_TO_DISTINGUISH' if len(distinct)>1 else
                    'NO_DIVERGENT_FROZEN_CONTINUATION_FOUND')
                prefix_audit.append(dict(schedule=name,event=row['event'],relation=f"{row['state']}:{row['action']}",
                    status=boundary,matching_frozen_schedules=peers,
                    available_relation_history=[list(x) for x in here if x[0]==row['state'] and x[1]==row['action']]))
            if before['kind']=='ESTABLISHED' and row['realized']!=before['established_value']:
                if after['kind']!='UNRESOLVED_CHANGE':missed+=1
                kind=('change' if row['phase']=='CHANGE' else 'anomaly' if row['phase']=='NOISE'
                      else 'restoration' if row['phase']=='RESTORATION' else 'excursion')
                confirmation=next((later['event']-row['event'] for later in rows[i+1:]
                    if later['state']==row['state'] and later['action']==row['action']
                    and later['grounded_state_after']['kind']=='ESTABLISHED'),None)
                transitions.append(dict(schedule=name,event=row['event'],kind=kind,
                    after_state=after['kind'],resolution_receipts=confirmation,
                    resolved_value=(next((later['grounded_state_after']['established_value']
                    for later in rows[i+1:] if later['state']==row['state'] and later['action']==row['action']
                    and later['grounded_state_after']['kind']=='ESTABLISHED'),None))))
            identities=[p['identity'] for p in after['receipt_provenance']]
            if len(identities)!=len(set(identities)) or len(identities)!=len([
                x for x in rows[:i+1] if x['state']==row['state'] and x['action']==row['action']]):
                provenance=False
    restart=json.loads((output/'schedules/SUSTAINED/stage-sustained2.json').read_text())['restart'] if complete else None
    perturb=json.loads((output/'schedules/SUSTAINED/perturbation.json').read_text()) if complete else None
    integrity=(complete and provenance and restart and restart['status']=='PASS' and perturb and
        perturb['status']=='PASS' and costs['U']['logical_model_calls']==0 and
        all(t['after_state']=='UNRESOLVED_CHANGE' and t['resolution_receipts']==1 for t in transitions))
    classification='EXPLICIT_UNCERTAINTY_SUPPORTED' if integrity and missed==0 else 'INVALID'
    result=dict(status='COMPLETE' if complete else 'STOPPED',classification=classification,
        schedules=list(SCHEDULES),events_per_arm=EVENTS_PER_ARM,conditions=list(ARMS),
        totals=totals,cold_start=cold,costs=costs,
        uncertainty=dict(established_pre_events=len(established),
            established_pre_correct=sum(r['realized']==r['grounded_state_before']['established_value'] for r in established),
            unresolved_pre_events=len(unresolved_pre),
            unresolved_pre_new_value=sum(r['realized']==r['grounded_state_before']['candidate_value'] for r in unresolved_pre),
            unresolved_pre_old_value=sum(r['realized']==r['grounded_state_before']['established_value'] for r in unresolved_pre),
            post_established_events=post_established,post_unresolved_events=post_unresolved,
            false_certainty_count=sum(r['realized']!=r['grounded_state_before']['established_value'] for r in established),
            missed_ambiguity_count=missed,transitions=transitions,
            provenance_integrity=provenance,restart_integrity=bool(restart and restart['status']=='PASS')),
        information_boundary_audit=prefix_audit,restart=restart,perturbation=perturb,
        model_call_ceiling=dict(logical=MODEL_LOGICAL_CEILING,physical=MODEL_PHYSICAL_CEILING),
        limitations=['Small deterministic protected simulation; no population inference.',
            'Hidden regime labels are known only for scoring; receipt-only U does not see them.',
            'Two consecutive identical receipts confirm by rule but cannot prove indefinite persistence.',
            'Forced point accuracy does not measure epistemic state quality.',
            'No additional context was given to M for contradictory histories.'])
    (output/'results.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    return result
if __name__=='__main__':
    p=ArgumentParser();p.add_argument('--output',type=Path,required=True)
    print(json.dumps(analyze(p.parse_args().output),sort_keys=True))
