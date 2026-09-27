"""Prospectively defined descriptive scoring of original protected receipts."""
from argparse import ArgumentParser
from collections import Counter
import json
from pathlib import Path
from statistics import mean
from horus.live import SessionStore
from .protocol import ARMS,SCHEDULES,MODEL_LOGICAL_CEILING,MODEL_PHYSICAL_CEILING


def accuracy(rows):
    n=len(rows)
    return dict(n=n,consequence_correct=sum(r['consequence_correct'] for r in rows),
        consequence_accuracy=sum(r['consequence_correct'] for r in rows)/n if n else None,
        exact_correct=sum(r['exact_correct'] for r in rows),
        exact_accuracy=sum(r['exact_correct'] for r in rows)/n if n else None)


def latency(rows,start,end):
    return next((r['event']-start for r in rows if start<=r['event']<=end
                 and r['consequence_correct']),None)


def transition_windows(name):
    if name=='A':return dict(change=(5,8),restoration=(9,12))
    if name=='C':return dict(change=(9,12))
    if name=='D':return dict(change=(5,10),restoration=(11,14))
    return {}


def summarize(name,rows):
    specs=SCHEDULES[name];n=len(rows)
    if [r['event'] for r in rows]!=[s['event'] for s in specs]:
        raise RuntimeError('incomplete or misordered scored events')
    thirds=dict(early=accuracy(rows[:n//3]),middle=accuracy(rows[n//3:2*n//3]),
                late=accuracy(rows[2*n//3:]))
    phases={phase:accuracy([r for r in rows if r['phase']==phase])
            for phase in dict.fromkeys(s['phase'] for s in specs)}
    transitions={kind:dict(first_event=start,last_event=end,
        first_correct_latency=latency(rows,start,end),
        correct=sum(r['consequence_correct'] for r in rows if start<=r['event']<=end),
        false_persistence=sum((not r['consequence_correct']) and
            r['prediction']['consequence']==rows[start-2]['realized']['consequence']
            for r in rows if start<=r['event']<=end))
        for kind,(start,end) in transition_windows(name).items()}
    rolling=[dict(start_event=rows[i]['event'],**accuracy(rows[i:i+4]))
             for i in range(max(0,n-3))]
    noise=next((r for r in rows if r['phase']=='NOISE'),None)
    recovery=next((r for r in rows if noise is not None and
                   r['event']==noise['event']+1),None)
    noise_metrics=(None if noise is None else dict(
        event=noise['event'],prediction_error=not noise['consequence_correct'],
        immediate_recovery_event=recovery['event'],
        immediate_recovery_error=not recovery['consequence_correct'],
        false_regime_switch=(recovery['prediction']['consequence']==
            noise['realized']['consequence'] and not recovery['consequence_correct'])))
    return dict(**accuracy(rows),cold_start=dict(**accuracy(rows[:1]),
        fallback_used=rows[0]['rule']=='COLD_START_NEUTRAL_ZERO_AND_IDENTITY_STATE'),
        post_cold_start=accuracy(rows[1:]),phases=phases,thirds=thirds,
        transitions=transitions,isolated_noise=noise_metrics,
        worst_rolling_four=min(rolling,key=lambda r:r['consequence_accuracy'])
                            if rolling else None,
        model_calls=sum(r['model_calls'] for r in rows),
        context_tokens=sum(r['context_tokens'] for r in rows),
        prediction_seconds=sum(r['model_seconds'] for r in rows),
        mean_prediction_seconds=mean(r['model_seconds'] for r in rows))


def current_phase_start(name,event):
    if name=='A':return 9 if event>=9 else 5 if event>=5 else 1
    if name=='B':return 6 if event>=6 else 5 if event==5 else 1
    if name=='C':return 9 if event>=9 else 6 if event>=6 else 5 if event==5 else 1
    if name=='D':return 11 if event>=11 else 5 if event>=5 else 1
    raise RuntimeError('unknown schedule')


def audit_errors(name,rows_by_arm):
    audit={arm:[] for arm in ARMS}
    actual={r['event']:r for r in rows_by_arm['M']}
    for arm in ARMS:
        rows=rows_by_arm[arm]
        for row in rows:
            if row['consequence_correct']:continue
            event=row['event'];truth=row['realized']['consequence']
            prior=[r for r in rows if r['event']<event]
            supplied=(row['selected_consequences'] if arm=='M' else
                row['window_consequences'] or [])
            recent=[r['realized']['consequence'] for r in prior[-3:]]
            current=[r for r in prior if r['event']>=current_phase_start(name,event)
                     and r['phase']!='NOISE' and r['realized']['consequence']==truth]
            if arm=='M':
                flags=dict(CORRECT_CURRENT_SIGNAL_PRESENT=bool(current) and
                    truth in supplied,
                    STALE_SIGNAL_DOMINATED=supplied.count(row['prediction']['consequence'])>
                        supplied.count(truth),
                    AMBIGUOUS_HISTORY=len(set(supplied))>1,
                    NO_RELEVANT_HISTORY=not prior,
                    MODEL_WRONG_DESPITE_CLEAR_GROUNDED_SIGNAL=(len(recent)==3 and
                        len(set(recent))==1 and recent[0]==truth))
                audit[arm].append(dict(schedule=name,event=event,flags=flags,
                    prediction=row['prediction']['consequence'],realized=truth,
                    supplied_consequences=supplied,
                    supplied_memory_identities=row['model_supplied_memories'],
                    prior_current_phase_correct_events=[r['event'] for r in current],
                    recent_exact_consequences=recent))
            else:
                previous_noise=bool(prior and prior[-1]['phase']=='NOISE')
                if not prior or row['phase']=='NOISE' or (
                    row['phase'] in ('CHANGE','RESTORATION') and
                    event==current_phase_start(name,event)):
                    cause='INSUFFICIENT_HISTORY'
                elif previous_noise and row['prediction']['consequence']==prior[-1]['realized']['consequence']:
                    cause='LATEST_OUTCOME_WAS_NOISE'
                elif arm=='R3' and row['rule']=='RECENT3_TIE_MOST_RECENT':
                    cause='TIE_RULE_ERROR'
                elif (row['phase'] in ('PERSISTENCE','RESTORATION') and
                      event-current_phase_start(name,event)<=2):
                    cause='WINDOW_TOO_SLOW'
                else:cause='OTHER_MECHANICAL'
                audit[arm].append(dict(schedule=name,event=event,cause=cause,
                    prediction=row['prediction']['consequence'],realized=truth,
                    window_consequences=row['window_consequences'],
                    used_event_identities=row['used_event_identities'],
                    recent_exact_consequences=recent))
    return audit


def classify(rows,per_schedule,integrity):
    if not integrity:return 'INVALID'
    noise_advantage=sum(per_schedule[n]['R3']['isolated_noise']['immediate_recovery_error']
        <per_schedule[n]['L']['isolated_noise']['immediate_recovery_error']
        for n in ('B','C'))
    latency_pairs=[]
    for name in ('A','C','D'):
        for phase in transition_windows(name):
            l=per_schedule[name]['L']['transitions'][phase]['first_correct_latency']
            r=per_schedule[name]['R3']['transitions'][phase]['first_correct_latency']
            if l is not None and r is not None:latency_pairs.append((l,r))
    faster=(latency_pairs and all(l<=r for l,r in latency_pairs)
            and any(l<r for l,r in latency_pairs))
    if faster and noise_advantage and any(
        per_schedule[n]['L']['isolated_noise']['immediate_recovery_error']
        >per_schedule[n]['R3']['isolated_noise']['immediate_recovery_error']
        for n in ('B','C')):
        return 'SPEED_ROBUSTNESS_TRADEOFF'
    for arm in ('L','R3'):
        comparisons=[]
        for name in SCHEDULES:
            # First event is explicitly outside head-to-head classification.
            comparisons.append((per_schedule[name][arm]['post_cold_start']['consequence_accuracy'],
                per_schedule[name]['M']['post_cold_start']['consequence_accuracy']))
            for phase in ('CHANGE','PERSISTENCE','RESTORATION','NOISE','RECOVERY'):
                if phase in per_schedule[name][arm]['phases']:
                    a=[r for r in rows[name][arm] if r['phase']==phase and r['event']!=1]
                    m=[r for r in rows[name]['M'] if r['phase']==phase and r['event']!=1]
                    comparisons.append((accuracy(a)['consequence_accuracy'],
                                        accuracy(m)['consequence_accuracy']))
        if all(a>=m for a,m in comparisons) and any(a>m for a,m in comparisons):
            return 'MECHANICAL_GROUNDING_SUFFICIENT'
    settings=set()
    for name in SCHEDULES:
        for m,l,r in zip(rows[name]['M'],rows[name]['L'],rows[name]['R3']):
            if m['event']>1 and m['consequence_correct'] and not l['consequence_correct'] and not r['consequence_correct']:
                settings.add((name,m['phase']))
    if len(settings)>=2:return 'MODEL_INTERPRETATION_ADDS_VALUE'
    return 'MIXED'


def analyze(output):
    rows={};per_schedule={};audit={arm:[] for arm in ARMS};operations={arm:dict(
        logical_model_calls=0,physical_transport_attempts=0,transport_failures=0,
        repaired_calls=0,unrepaired_failures=0,model_invalid_outputs=0,
        intentional_parser_rejections=0,context_tokens=0,model_seconds=0.0,
        prediction_seconds=0.0) for arm in ARMS}
    stops=[];restarts={};perturbations={};wall_seconds=0.0
    for name,specs in SCHEDULES.items():
        root=output/'schedules'/name
        rows[name]={}
        for arm in ARMS:
            with SessionStore(root/arm/'session',True) as store:
                rows[name][arm]=[e['record'] for e in store.records['training']
                    if e['kind']=='GROUNDED_REDUCER_SCORED_EVENT']
                calls=store.records['calls'];op=operations[arm]
                intents=[e['record'] for e in calls if e['kind']=='REQUEST_INTENT']
                attempts=[e['record'] for e in calls if e['kind']=='TRANSPORT_ATTEMPT_RESULT']
                parsed=[e['record'] for e in calls if e['kind']=='PARSED']
                injected={e['record']['call_id'] for e in calls if e['kind']=='RESPONSE'
                          and e['record'].get('fault_injected')}
                op['logical_model_calls']+=len(intents)
                op['physical_transport_attempts']+=len(attempts)
                op['transport_failures']+=sum(a['outcome']=='TRANSPORT_FAILURE' for a in attempts)
                op['repaired_calls']+=sum(a['repaired'] for a in attempts)
                op['unrepaired_failures']+=sum(a['unrepaired'] for a in attempts)
                op['model_invalid_outputs']+=sum(p['outcome']=='MODEL_OUTPUT_INVALID'
                    and p['call_id'] not in injected for p in parsed)
                op['intentional_parser_rejections']+=len(injected)
                op['model_seconds']+=sum(a['seconds'] for a in attempts)
                op['prediction_seconds']+=sum(r['model_seconds'] for r in rows[name][arm])
                op['context_tokens']+=sum(r['context_tokens'] for r in rows[name][arm])
        if (root/'stop.json').exists():stops.append(json.loads((root/'stop.json').read_text()))
        if name=='A':
            if (root/'stage-a2.json').exists():
                restarts[name]=json.loads((root/'stage-a2.json').read_text())['restart']
            if (root/'perturbation.json').exists():
                perturbations[name]=json.loads((root/'perturbation.json').read_text())
                operations['M']['context_tokens']+=perturbations[name]['context_tokens']
                operations['M']['prediction_seconds']+=perturbations[name]['model_seconds']
        for stage in (('A1','A2') if name=='A' else (name,)):
            path=root/('before-restart.json' if stage=='A1' else f'stage-{stage.lower()}.json')
            if path.exists():wall_seconds+=json.loads(path.read_text())['wall_seconds']
        if all(len(rows[name][arm])==len(specs) for arm in ARMS):
            per_schedule[name]={arm:summarize(name,rows[name][arm]) for arm in ARMS}
            part=audit_errors(name,rows[name])
            for arm in ARMS:audit[arm].extend(part[arm])
    complete=(output/'campaign-complete.json').exists() and len(per_schedule)==4 and not stops
    classification=classify(rows,per_schedule,complete) if complete else 'INVALID'
    totals={arm:accuracy([r for name in SCHEDULES for r in rows[name][arm]]) for arm in ARMS}
    for arm in ARMS:
        operations[arm]['completion_rate']=(1-operations[arm]['unrepaired_failures']/operations[arm]['logical_model_calls']
            if operations[arm]['logical_model_calls'] else 1.0)
        operations[arm]['mean_prediction_seconds']=(operations[arm]['prediction_seconds']/sum(map(len,SCHEDULES.values())))
    result=dict(status='COMPLETE' if complete else 'STOPPED',classification=classification,
        conditions=list(ARMS),schedules=list(SCHEDULES),events_per_arm=sum(map(len,SCHEDULES.values())),
        totals=totals,per_schedule=per_schedule,error_audit=audit,operational=operations,
        call_ceiling=dict(logical=MODEL_LOGICAL_CEILING,physical=MODEL_PHYSICAL_CEILING),
        restart=restarts,perturbation=perturbations,worker_wall_seconds=wall_seconds,
        stops=stops,limitations=[
            'Four small deterministic simulated sequences and one frozen model family; no population inference.',
            'The isolated anomaly uses a one-event hidden regime override; other noise types are untested.',
            'All actions are observation-controlled HOLD, so autonomy and unseen relations are outside this comparison.',
            'Cold-start fallback is a neutral consequence and identity next-state assumption, scored separately.',
            'Single machine service latency can vary; model inference time is observational.',
            'Atomicity is committed visibility of simulated worlds, not simultaneous physical actuation.'])
    (output/'results.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    return result

if __name__=='__main__':
    p=ArgumentParser();p.add_argument('--output',type=Path,required=True)
    print(json.dumps(analyze(p.parse_args().output),sort_keys=True))
