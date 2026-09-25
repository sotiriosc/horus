"""Frozen explicit-policy targets, paired correctness and family gates."""
from collections import Counter
from experiments.model_explorer_semantic_prior_study_v0.adapter import parse_surface
ARMS=('CONTROL','CHANGED');CONDITIONS=('A','B');ACTIONS=('HOLD','RETREAT','ADVANCE','invalid')

def score(raw,mapping,target):
    surface,action,error=parse_surface(raw,dict(surface_option_order=list(mapping),surface_to_underlying=mapping))
    return dict(valid=action is not None,surface=surface,action=action,error=error,category=action or 'invalid',mean_policy_correct=action==target)

def cell(rows):
    return dict(calls=len(rows),valid=sum(r['scoring']['valid'] for r in rows),
        counts={k:sum(r['scoring']['category']==k for r in rows) for k in ACTIONS},mean_policy_correct=sum(r['scoring']['mean_policy_correct'] for r in rows))

def sensitivity(a,b):
    if 'invalid' in (a,b):return 'invalid_in_pair'
    if a==b:return 'same_action'
    if (a,b) in (('HOLD','RETREAT'),('ADVANCE','RETREAT'),('RETREAT','HOLD'),('RETREAT','ADVANCE')):return a+'_to_'+b
    return 'other'

def pairs(rows):
    out=[]
    for f in ('O1','O2'):
        for j in range(12):
            for arm in ARMS:
                rs=[r for r in rows if r['descriptor']['family']==f and r['descriptor']['schedule']==j and r['descriptor']['arm']==arm]
                scores={c:next(r['scoring'] for r in rs if r['descriptor']['condition']==c) for c in CONDITIONS}
                a,b=scores['A'],scores['B'];target=rs[0]['intent']['audit']['policy_calculation']['unique_target']
                # Invalid is never a target selection; always retained in denominators.
                favorable=a['action']!=target and b['action']==target;reverse=a['action']==target and b['action']!=target
                out.append(dict(family=f,schedule=j,mapping_index=j%6,mapping=rs[0]['descriptor']['mapping'],seed=94001+j,arm=arm,target=target,
                    conditions=scores,sensitivity=sensitivity(a['category'],b['category']),favorable=favorable,reverse=reverse,
                    invalid_in_pair=not(a['valid'] and b['valid']),favorable_both_valid=favorable and a['valid'] and b['valid'],reverse_both_valid=reverse and a['valid'] and b['valid']))
    return out

def criteria(cells,paired,integrity,replay):
    return dict(all_B_calls_complete=cells['CONTROL/B']['calls']==cells['CHANGED/B']['calls']==12,
        B_valid_at_least_23=cells['CONTROL/B']['valid']+cells['CHANGED/B']['valid']>=23,
        CONTROL_B_HOLD_at_least_10=cells['CONTROL/B']['counts']['HOLD']>=10,
        CHANGED_B_RETREAT_at_least_10=cells['CHANGED/B']['counts']['RETREAT']>=10,
        CHANGED_favorable_at_least_8=paired['favorable']>=8,CHANGED_reverse_at_most_1=paired['reverse']<=1,
        histories_authentic=integrity,old_and_new_records_unchanged=integrity,model_sampler_parser_integrity=integrity,exact_replay=replay)

def summarize(rows,replay=None):
    ps=pairs(rows);families={}
    for f in ('O1','O2'):
        fr=[r for r in rows if r['descriptor']['family']==f];fp=[p for p in ps if p['family']==f]
        cells={a+'/'+c:cell([r for r in fr if r['descriptor']['arm']==a and r['descriptor']['condition']==c]) for a in ARMS for c in CONDITIONS}
        paired={a:{k:sum(p[k] for p in fp if p['arm']==a) for k in ('favorable','reverse','invalid_in_pair','favorable_both_valid','reverse_both_valid')} for a in ARMS}
        integrity=all(r['intent']['audit']['passed'] and r['intent']['audit']['mean_target_unique'] and r['intent']['audit']['old_records_present_unchanged'] and r['intent']['audit']['new_records_present_unchanged'] for r in rows)
        gates=criteria(cells,paired['CHANGED'],integrity,replay);supported=all(v is True for v in gates.values())
        families[f]=dict(cells=cells,paired=paired,criteria=gates,supported=supported,decision='EXPLICIT-MEAN EXPLORER POLICY '+('SUPPORTED' if supported else 'NOT ESTABLISHED'),
            output_sensitivity={a:dict(Counter(p['sensitivity'] for p in fp if p['arm']==a)) for a in ARMS})
    return dict(study='explorer-value-aggregation-contract-v0',completed_calls=len(rows),valid_responses=sum(r['scoring']['valid'] for r in rows),
        Explorer_calls=len(rows),Map_calls=0,Recovery_model_calls=0,measured_world_executions=0,measured_Memory_commits=0,
        deterministic_setup_events=8*len(rows),native_state_Recovery_calls=sum(r['intent']['audit']['native_state_Recovery_calls'] for r in rows),
        native_measurement_Recovery_calls=sum(r['intent']['audit']['native_measurement_Recovery_calls'] for r in rows),
        families=families,pairs=ps,status='FINAL' if replay is True else 'AWAITING_EXACT_REPLAY_AND_PRESERVATION',
        classification='EXPLICIT-MEAN EXPLORER POLICY '+('REPLICATED' if all(f['supported'] for f in families.values()) else 'NOT ESTABLISHED'))
