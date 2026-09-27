"""Separate forecast, comparison and composed-choice diagnostics."""
from collections import Counter
from .contexts import ACTIONS,WORLDS

def classify(d,map_calls,oracle,choices):
    truth=oracle['values'];best=max(ACTIONS,key=lambda a:truth[a]['consequence'])
    scores=[]
    for a,call in zip(ACTIONS,map_calls):
        p=call['parsed'];valid=p is not None
        scores.append(dict(action=a,alias=next(k for k,v in d['mapping'].items() if v==a),prediction=p,truth=truth[a],valid=valid,
            exact=valid and p==truth[a],state_correct=valid and p['next_state']==truth[a]['next_state'],consequence_correct=valid and p['consequence']==truth[a]['consequence']))
    if not all(s['valid'] for s in scores):ranking='INVALID/MISSING';maximum=None
    else:
        values={s['action']:s['prediction']['consequence'] for s in scores};maximums=[a for a,v in values.items() if v==max(values.values())]
        maximum=maximums[0] if len(maximums)==1 else None
        ranking='TIED_MAXIMUM' if maximum is None else 'TRUE_BEST_UNIQUE_MAX' if maximum==best else 'WRONG_ACTION_UNIQUE_MAX'
    out={}
    for label in ('Oracle','Permutation','ModelMap'):
        action=choices.get(label)
        out[label]=dict(issued=label in choices,action=action,valid=action is not None,true_best=action==best,
            follows_Map=label=='ModelMap' and action is not None and action==maximum)
    m=out['ModelMap'];eligible=maximum is not None
    if ranking=='INVALID/MISSING':failure='MAP_INVALID_NO_EXPLORER'
    elif ranking=='TIED_MAXIMUM':failure='MAP_TIE_NO_EXPLORER'
    elif not m['valid']:failure='EXPLORER_INVALID'
    elif ranking=='TRUE_BEST_UNIQUE_MAX':failure='MAP_CORRECT_EXPLORER_CORRECT' if m['true_best'] else 'MAP_CORRECT_EXPLORER_WRONG'
    else:failure='MAP_WRONG_EXPLORER_FOLLOWS_MAP' if m['follows_Map'] else 'MAP_WRONG_EXPLORER_DISAGREES'
    base,perm=out['Oracle'],out['Permutation'];comparable=base['valid'] and perm['valid']
    return dict(descriptor=d,map_scores=scores,true_best=best,map_max=maximum,ranking=ranking,eligible=eligible,choices=out,
        end_to_end=eligible and m['valid'] and m['true_best'],failure_source=failure,
        permutation_same=comparable and base['action']==perm['action'],permutation_changed=comparable and base['action']!=perm['action'],permutation_not_comparable=not comparable)

def acc(scores):return dict(n=len(scores),**{k:sum(s[k] for s in scores) for k in ('valid','exact','state_correct','consequence_correct')})
def cell(rows):
    eligible=[r for r in rows if r['eligible']];mc=[r['choices']['ModelMap'] for r in eligible]
    ratio=lambda n,d:dict(numerator=n,denominator=d,rate=None if d==0 else n/d)
    ratios=dict(eligible_over_contexts=ratio(len(eligible),len(rows)),issued_over_contexts=ratio(sum(x['issued'] for x in mc),len(rows)),valid_over_contexts=ratio(sum(x['valid'] for x in mc),len(rows)),valid_over_issued=ratio(sum(x['valid'] for x in mc),sum(x['issued'] for x in mc)),followed_Map_over_valid_issued=ratio(sum(x['follows_Map'] for x in mc),sum(x['valid'] for x in mc)))
    return dict(contexts=len(rows),descriptive_ratios=ratios,Map=acc([s for r in rows for s in r['map_scores']]),
        rankings=dict(Counter(r['ranking'] for r in rows)),eligible=len(eligible),ties=sum(r['ranking']=='TIED_MAXIMUM' for r in rows),
        Oracle=dict(issued=sum(r['choices']['Oracle']['issued'] for r in rows),valid=sum(r['choices']['Oracle']['valid'] for r in rows),true_best=sum(r['choices']['Oracle']['true_best'] for r in rows),actions=dict(Counter(r['choices']['Oracle']['action'] or 'INVALID' for r in rows))),
        Permutation=dict(issued=sum(r['choices']['Permutation']['issued'] for r in rows),valid=sum(r['choices']['Permutation']['valid'] for r in rows),true_best=sum(r['choices']['Permutation']['true_best'] for r in rows),same=sum(r['permutation_same'] for r in rows),changed=sum(r['permutation_changed'] for r in rows),not_comparable=sum(r['permutation_not_comparable'] for r in rows)),
        ModelMap=dict(issued=sum(x['issued'] for x in mc),valid=sum(x['valid'] for x in mc),follows_Map=sum(x['follows_Map'] for x in mc),true_best=sum(x['true_best'] for x in mc),
            disagreements=sum(x['valid'] and not x['follows_Map'] for x in mc),actions=dict(Counter(x['action'] or 'INVALID' for x in mc))),
        end_to_end=sum(r['end_to_end'] for r in rows),failures=dict(Counter(r['failure_source'] for r in rows)),
        oracle_to_composed_loss=sum(r['choices']['Oracle']['true_best'] for r in rows)-sum(r['end_to_end'] for r in rows))

def summarize(contexts,calls,replay=None):
    rows=[c['result'] for c in contexts];families={}
    integrity=all(c['audit_after']['passed'] and c['protected_unchanged'] and c['oracle_after_all_Map_parses'] for c in contexts)
    for family in ('O1','O2'):
        rr=[r for r in rows if r['descriptor']['family']==family];allc=cell(rr);worlds={w:cell([r for r in rr if r['descriptor']['world']==w]) for w in WORLDS}
        oracle=allc['Oracle'];perm=allc['Permutation'];model=allc['ModelMap'];rank=allc['rankings']
        A=dict(all_24_complete=oracle['issued']==24,valid_at_least_23=oracle['valid']>=23,total_best_at_least_20=oracle['true_best']>=20,
            **{w+'_best_at_least_5':worlds[w]['Oracle']['true_best']>=5 for w in WORLDS},integrity=integrity,exact_replay=replay)
        B=dict(all_72_Map_complete=allc['Map']['n']==72,valid_at_least_69=allc['Map']['valid']>=69,unique_max_at_least_20=allc['eligible']>=20,
            true_best_unique_at_least_18=rank.get('TRUE_BEST_UNIQUE_MAX',0)>=18,
            **{w+'_best_unique_at_least_4':worlds[w]['rankings'].get('TRUE_BEST_UNIQUE_MAX',0)>=4 for w in WORLDS},no_oracle_leakage=integrity,exact_replay=replay)
        C=dict(eligible_at_least_18=allc['eligible']>=18,all_eligible_calls_complete=model['issued']==allc['eligible'],valid_at_least_17=model['valid']>=17,
            validity_at_least_90pct=model['issued']>0 and model['valid']*10>=model['issued']*9,
            follows_at_least_90pct_valid=model['valid']>0 and model['follows_Map']*10>=model['valid']*9,
            no_world_over_two_disagreements=all(worlds[w]['ModelMap']['disagreements']<=2 for w in WORLDS),exact_replay=replay)
        N=dict(all_24_complete=perm['issued']==24,valid_at_least_23=perm['valid']>=23,same_at_least_22=perm['same']>=22,
            best_at_least_20=perm['true_best']>=20,no_world_below_5=all(worlds[w]['Permutation']['true_best']>=5 for w in WORLDS))
        gates={'A_ORACLE_COMPARISON':A,'B_MAP_RANKING':B,'C_EXPLORER_FOLLOWS_MAP':C,'NEXT_STATE_CONTROL':N}
        decisions={k:dict(criteria=g,supported=all(v is True for v in g.values()),decision='SUPPORTED' if all(v is True for v in g.values()) else 'NOT ESTABLISHED') for k,g in gates.items()}
        decisions['C_EXPLORER_FOLLOWS_MAP']['reason']=('INSUFFICIENT_ELIGIBLE_CONTEXTS' if allc['eligible']<18 else 'SUPPORTED' if decisions['C_EXPLORER_FOLLOWS_MAP']['supported'] else 'FROZEN_FOLLOWING_CRITERION_NOT_MET')
        scores=[(r,s) for r in rr for s in r['map_scores']]
        families[family]=dict(total=allc,worlds=worlds,decisions=decisions,
            by_mapping={str(j):cell([r for r in rr if r['descriptor']['mapping_index']==j]) for j in range(6)},
            Map_by_action={a:acc([s for r,s in scores if s['action']==a]) for a in ACTIONS},
            Map_by_alias={a:acc([s for r,s in scores if s['alias']==a]) for a in rr[0]['descriptor']['mapping']} if rr else {},
            by_true_best_alias={a:cell([r for r in rr if r['descriptor']['mapping'][a]==r['true_best']]) for a in rr[0]['descriptor']['mapping']} if rr else {})
    stages={k:all(families[f]['decisions'][k]['supported'] for f in ('O1','O2')) for k in ('A_ORACLE_COMPARISON','B_MAP_RANKING','C_EXPLORER_FOLLOWS_MAP')}
    return dict(study='map-explorer-oracle-decomposition-v0',completed_contexts=len(rows),mandatory_calls=sum(c['slot']!='ModelMap' for c in calls),
        Map_calls=sum(c['slot'].startswith('Map:') for c in calls),Oracle_Explorer_calls=sum(c['slot']=='Oracle' for c in calls),Permutation_Explorer_calls=sum(c['slot']=='Permutation' for c in calls),
        conditional_eligible_contexts=sum(r['eligible'] for r in rows),conditional_calls=sum(c['slot']=='ModelMap' for c in calls),total_calls=len(calls),
        skipped_tie_slots=sum(r['ranking']=='TIED_MAXIMUM' for r in rows),skipped_invalid_slots=sum(r['ranking']=='INVALID/MISSING' for r in rows),Recovery_model_calls=0,
        measured_choice_executions=0,measured_receipts=0,measured_Memory_commits=0,
        detached_oracle_evaluations=3*len(rows),families=families,contexts=rows,total=cell(rows),stage_replication=stages,
        failed_stages=[k for k,v in stages.items() if not v],
        classification='MAP→EXPLORER DECOMPOSED PIPELINE SUPPORTED FOR THE REGISTERED UNIQUE-BEST FIXTURES' if all(stages.values()) else 'PIPELINE NOT FULLY ESTABLISHED',
        status='FINAL' if replay is True else 'AWAITING_EXACT_REPLAY_AND_PRESERVATION',temporal_prior='MAP TEMPORAL-RELATION FORECASTING BEYOND PURE RECENCY NOT ESTABLISHED')
