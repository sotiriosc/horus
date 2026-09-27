"""Descriptive frozen comparison; operational failures never count as bad predictions."""
from argparse import ArgumentParser
from collections import Counter
import json
from pathlib import Path
from horus.live import SessionStore
from .storage import ModernMemory
from .transport import RULE_HASH


def summarize(rows, abstentions):
    a = [r for r in rows if r['stage']=='A']
    b = [r for r in rows if r['stage']=='B']
    def accuracy(part):
        return dict(n=len(part), consequence_correct=sum(r['consequence_correct'] for r in part),
            exact_correct=sum(r['exact_correct'] for r in part),
            consequence_accuracy=sum(r['consequence_correct'] for r in part)/len(part) if part else None,
            exact_accuracy=sum(r['exact_correct'] for r in part)/len(part) if part else None)
    windows={name:accuracy([r for r in a if lo<=r['event']<=hi]) for name,lo,hi in
             [('stable',1,4),('change',5,8),('restoration',9,12)]}
    def latency(lo,hi):
        return next((r['event']-lo for r in a if lo<=r['event']<=hi and r['consequence_correct']),None)
    wrong=[r['event'] for r in a if r['realized']['consequence'] in r['retrieval'][r['action']]['selected_consequences'] and not r['consequence_correct']]
    rolling=[dict(start_event=a[i]['event'],**accuracy(a[i:i+4])) for i in range(len(a)-3)]
    return dict(stage_a=dict(**accuracy(a),windows=windows,
        adaptation_latency=latency(5,8),restoration_latency=latency(9,12),
        false_persistence=sum(not r['consequence_correct'] for r in a if 5<=r['event']<=8),
        correct_memory_model_wrong_events=wrong,
        worst_rolling_four=min(rolling,key=lambda r:r['consequence_accuracy']) if rolling else None,
        realized_total=sum(r['realized']['consequence'] for r in a)),
        stage_b=dict(**accuracy(b),decisions=len(b)+len(abstentions),
            actions=[r['action'] for r in b],abstentions=abstentions,
            realized_total=sum(r['realized']['consequence'] for r in b),
            trajectory=sorted(b+abstentions,key=lambda r:r['event'])))


def analyze(output):
    conditions={}; rows={}; calls={}; memory_rows={}; operations={}
    for arm in ('M','MH'):
        with SessionStore(output/arm/'session',True) as store, ModernMemory(output/arm/'memory.sqlite3',False) as memory:
            rows[arm]=[e['record'] for e in store.records['training'] if e['kind']=='MODERN_VS_HORUS_SCORED_EVENT']
            abstentions=[e['record'] for e in store.records['training'] if e['kind']=='AUTONOMOUS_ABSTENTION']
            calls[arm]=store.records['calls']; memory_rows[arm]=memory.rows()
            conditions[arm]=summarize(rows[arm],abstentions)
        c=calls[arm]
        intents=[e['record'] for e in c if e['kind']=='REQUEST_INTENT']
        attempts=[e['record'] for e in c if e['kind']=='TRANSPORT_ATTEMPT_RESULT']
        parsed=[e['record'] for e in c if e['kind']=='PARSED']
        injected={e['record']['call_id'] for e in c if e['kind']=='RESPONSE' and e['record']['fault_injected']}
        failures=[e for e in attempts if e['outcome']=='TRANSPORT_FAILURE']
        unrepaired=[e for e in attempts if e['unrepaired']]
        model_invalid=[e for e in parsed if e['outcome']=='MODEL_OUTPUT_INVALID' and e['call_id'] not in injected]
        operations[arm]=dict(logical_model_calls=len(intents),physical_transport_attempts=len(attempts),
            transport_failures=len(failures),repaired_calls=sum(e['repaired'] for e in attempts),
            unrepaired_failures=len(unrepaired),model_invalid_outputs=len(model_invalid),
            registered_injected_invalid_outputs=len(injected),
            completed_responses=sum(e['outcome']=='RESPONSE_RECEIVED' for e in attempts),
            completion_rate=sum(e['outcome']=='RESPONSE_RECEIVED' for e in attempts)/len(intents) if intents else None,
            scheduled_stage_a_completion_rate=conditions[arm]['stage_a']['n']/12,
            model_seconds=sum(e['seconds'] for e in attempts),
            active_wall_seconds=sum(e['record']['seconds'] for e in c if e['kind']=='PREPARATION_GUARD')+
                sum(r['publication_seconds'] for r in rows[arm])+
                sum(r['model_seconds'] for r in rows[arm]+abstentions if r['stage']=='B'),
            failure_attempts=failures,context_tokens=sum(r['context_tokens'] for r in rows[arm])+sum(r['context_tokens'] for r in abstentions))
    def histories(arm,row):
        eligible=[r for r in memory_rows[arm] if r['relation']==f"{row['state']}:{row['action']}" and r['event_stream_sequence']<row['event_stream_sequence']]
        return dict(eligible_raw_history=eligible,supplied_history=row['memories_supplied_to_model'],
                    supplied_consequences=row['retrieval'][row['action']]['selected_consequences'])
    ledger=[]; bottleneck=[]
    for stage in ('A','B'):
        left={r['event']:r for r in rows['M'] if r['stage']==stage}
        right={r['event']:r for r in rows['MH'] if r['stage']==stage}
        for event in sorted(left.keys() & right.keys()):
            m,h=left[event],right[event]
            changed=m['prediction']!=h['prediction']
            if stage=='A':
                bottleneck.append(dict(event=event,
                    M_right_memory_present=m['realized']['consequence'] in m['retrieval'][m['action']]['selected_consequences'],
                    MH_right_memory_present=h['realized']['consequence'] in h['retrieval'][h['action']]['selected_consequences'],
                    M_model_correct=m['consequence_correct'],MH_model_correct=h['consequence_correct'],
                    horus_changed_output=changed,change_improved_reality_match=(h['consequence_correct'] and not m['consequence_correct']) if changed else None))
            candidate_changes=[action for action in m['public_forecasts'] if
                (m['public_forecasts'][action]['next_state'],m['public_forecasts'][action]['routed_consequence']) !=
                (h['public_forecasts'][action]['next_state'],h['public_forecasts'][action]['routed_consequence'])]
            if not changed and m['action']==h['action'] and not candidate_changes: continue
            delta=(int(h['consequence_correct'])-int(m['consequence_correct']) if stage=='A' else
                   h['realized']['consequence']-m['realized']['consequence'])
            mechanism=('SPECIALIST_ROUTING' if h['selected_specialist']!='G2' else
                       'EXPLORER_PROBE' if h['explorer']['mode']=='PROBE' else 'UNATTRIBUTED_OUTPUT_DIFFERENCE')
            ledger.append(dict(stage=stage,event=event,M=histories('M',m),MH=histories('MH',h),
                M_prediction=m['prediction'],MH_prediction=h['prediction'],
                M_action=m['action'],MH_action=h['action'],candidate_prediction_changes=candidate_changes,
                horus_mechanism=mechanism,realized_consequence=dict(M=m['realized'],MH=h['realized']),
                effect='IMPROVED' if delta>0 else 'DEGRADED' if delta<0 else 'NO_NET_EFFECT'))
    effects=Counter(r['effect'] for r in ledger)
    complete=(output/'campaign-complete.json').exists() and all(conditions[a]['stage_a']['n']==12 for a in conditions)
    stop=json.loads((output/'stop.json').read_text()) if (output/'stop.json').exists() else None
    classification=('INVALID' if not complete or stop else
        'HORUS_NET_HARMFUL' if effects['DEGRADED']>effects['IMPROVED'] else
        'MIXED_COMPONENT_SIGNAL' if effects['DEGRADED'] and effects['IMPROVED'] else
        'HORUS_DISTINCTLY_USEFUL' if effects['IMPROVED'] else 'MODERN_BASE_SUFFICIENT')
    routing=[r['routing_evidence'] for r in rows['MH'] if r['routing_evidence']]
    restart=json.loads((output/'stage-a2.json').read_text()).get('restart_verification') if (output/'stage-a2.json').exists() else None
    perturb=json.loads((output/'perturbation.json').read_text()) if (output/'perturbation.json').exists() else None
    for arm in operations:
        if perturb: operations[arm]['context_tokens']+=perturb[arm]['context_tokens']
    stages=[json.loads((output/name).read_text()) for name in ('before-restart.json','stage-a2.json','stage-b.json') if (output/name).exists()]
    result=dict(status='COMPLETE' if complete else 'STOPPED',classification=classification,
        stop=stop,conditions=conditions,operational_cost=operations,
        worker_wall_seconds=sum(s['wall_seconds'] for s in stages),
        transport_repair_rule_sha256=RULE_HASH,
        stage_a_invariant=json.loads((output/'current/pair.json').read_text()),
        interpretation_bottleneck=bottleneck,intervention_ledger=ledger,
        intervention_effect_counts=dict(effects),restart=restart,perturbation=perturb,
        horus_activity=dict(specialist_switches=sum(r['switch_occurred'] for r in routing),
            switch_records=[r for r in routing if r['switch_occurred']],
            explorer_probes=sum(r['explorer']['mode']=='PROBE' for r in rows['MH'] if r['stage']=='B'),
            problem_objects=0,route_executions=0,repair_recoveries=0,reacquisitions=0),
        limitations=['Single deterministic small simulated workload; descriptive, not population inference.',
            'Atomicity is committed snapshot visibility, not simultaneous irreversible external actuation.',
            'Private transaction workspace can contain a partial pair on commit failure; it is never published or resumed.',
            'Active arm wall time excludes waiting for the sibling and model loading; worker wall time includes both.',
            'Problem/route components remain dormant in this frozen harness.',
            'Right-memory metric means a matching consequence is supplied, not that the model understood its temporal relevance.'])
    (output/'results.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    return result

if __name__=='__main__':
    p=ArgumentParser();p.add_argument('--output',type=Path,required=True)
    print(json.dumps(analyze(p.parse_args().output),sort_keys=True))
