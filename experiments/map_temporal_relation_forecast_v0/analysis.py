"""Receipt-only scoring and frozen independent family gates."""
from collections import Counter
from .contexts import ARMS,SEQUENCES
PREFIX='MAP TEMPORAL-RELATION FORECASTING BEYOND PURE RECENCY '
def summarize(rows,replay=None):
    families={};pairs=[]
    for family in ('O1','O2'):
        fr=[r for r in rows if r['descriptor']['family']==family];cells={};fp=[]
        for arm in ARMS:
            rs=[r for r in fr if r['descriptor']['arm']==arm];scores=[r['outcome']['score'] for r in rs]
            cells[arm]=dict(calls=len(rs),**{k:sum(s[k] for s in scores) for k in ('valid','exact_match','consequence_match','state_match')},
                consequence_counts=dict(Counter(str(s['prediction']['consequence']) if s['valid'] else 'invalid' for s in scores)))
        for j in range(12):
            rr={r['descriptor']['arm']:r for r in fr if r['descriptor']['schedule']==j}
            if not all(a in rr for a in ('F','P')):continue
            fs,ps=[rr[a]['outcome']['score'] for a in ('F','P')]
            correct=[s['consequence_match'] for s in (fs,ps)]
            pred=[s['prediction']['consequence'] if s['valid'] else None for s in (fs,ps)]
            fp.append(dict(family=family,schedule=j,seed=95001+j,mapping=rr['F']['descriptor']['mapping'],mapping_index=j%6,
                F=dict(history=list(SEQUENCES['F'][:6]),**fs),P=dict(history=list(SEQUENCES['P'][:6]),**ps),
                category=('BOTH_CORRECT' if all(correct) else 'F_ONLY_CORRECT' if correct[0] else 'P_ONLY_CORRECT' if correct[1] else 'BOTH_WRONG'),
                same_consequence=pred[0] is not None and pred[0]==pred[1],latest_for_both=pred==[-1,-1]))
        counts={k:sum(p['category']==k for p in fp) for k in ('BOTH_CORRECT','F_ONLY_CORRECT','P_ONLY_CORRECT','BOTH_WRONG')}
        gates=dict(all_family_calls_complete=len(fr)==48,every_arm_valid_at_least_11=all(c['valid']>=11 for c in cells.values()),
            S_exact_at_least_10=cells['S']['exact_match']>=10,F_exact_at_least_9=cells['F']['exact_match']>=9,
            T_exact_at_least_9=cells['T']['exact_match']>=9,P_exact_at_least_9=cells['P']['exact_match']>=9,
            FP_both_correct_at_least_8=counts['BOTH_CORRECT']>=8,P_latest_minus1_at_most_2=cells['P']['consequence_counts'].get('-1',0)<=2,
            T_latest_minus1_at_most_2=cells['T']['consequence_counts'].get('-1',0)<=2,
            authentic_scored_receipts=all(not r['outcome']['score']['valid'] or r['outcome']['event']['full_provenance'][-1]['original_receipt_object'] for r in fr),
            no_future_leakage=all(r['intent']['audit']['future_reads']==0 for r in fr),integrity=all(r['outcome']['integrity'] for r in fr),exact_replay=replay)
        supported=all(v is True for v in gates.values());families[family]=dict(arms=cells,FP_counts=counts,criteria=gates,supported=supported,decision=PREFIX+('SUPPORTED' if supported else 'NOT ESTABLISHED'))
        pairs+=fp
    events=[r['outcome']['event'] for r in rows if r['outcome']['event']]
    scores=[r['outcome']['score'] for r in rows]
    baseline=[]
    for r in rows:
        s=r['outcome']['score'];h=[x['consequence'] for x in r['intent']['request_payload']['VERIFIED_CHRONOLOGICAL_HISTORY']]
        mean=sum(h)/len(h);sign=1 if mean>0 else -1 if mean<0 else None
        baseline.append(dict(index=r['index'],latest=h[-1],histogram={str(k):h.count(k) for k in (-1,1)},mean=mean,mean_sign=sign,
            receipt=s['actual'],latest_correct=s['actual'] is not None and h[-1]==s['actual']['consequence'],
            mean_sign_correct=None if sign is None or s['actual'] is None else sign==s['actual']['consequence']))
    return dict(study='map-temporal-relation-forecast-v0',completed_calls=len(rows),Map_calls=len(rows),Explorer_calls=0,Recovery_model_calls=0,
        valid_responses=sum(s['valid'] for s in scores),measured_events=len(events),setup_events=6*len(rows),
        measurement_mismatches=sum(not e['after']['protected']['memory'][-1]['measurement_matches'] for e in events),
        native_state_Recovery=sum(o['kind']=='recovery_state_proposal' for e in events for o in e['observed_recovery']),
        native_measurement_Recovery=sum(o['kind']=='recovery_measurement' for e in events for o in e['observed_recovery']),
        setup_measurement_mismatches=sum(r['setup_counts']['mismatches'] for r in rows),
        setup_native_state_Recovery=sum(r['setup_counts']['state_recovery'] for r in rows),
        setup_native_measurement_Recovery=sum(r['setup_counts']['measurement_recovery'] for r in rows),
        authorization_failures=sum(not e['result']['committed'] for e in events),families=families,FP_pairs=pairs,baselines=baseline,
        calls=[dict(descriptor=r['descriptor'],score=r['outcome']['score']) for r in rows],
        status='FINAL' if replay is True else 'AWAITING_REPLAY_AND_PRESERVATION',
        classification=PREFIX+('REPLICATED' if all(f['supported'] for f in families.values()) else 'NOT ESTABLISHED'))
