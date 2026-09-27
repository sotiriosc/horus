"""Prospective family gates, exact outcomes, matched trajectories and latency."""
from collections import Counter
from experiments.model_map_proposal_v0.adapter import parse
STAGES=('P0','P1','P2');ARMS=('CONTROL','CHANGED')

def score(raw,current):
    try:value=parse(raw)
    except (ValueError,TypeError) as exc:
        return dict(valid=False,prediction=None,error=str(exc),category='invalid',old_exact=False,new_exact=False,zero_exact=False,
            next_state_correct=False,consequence_correct=False,current_exact=False)
    pair=(value['next_state'],value['consequence']);cat={(1,1):'old',(1,-1):'new',(1,0):'zero'}.get(pair,'other_valid')
    ns=value['next_state']==current['next_state'];co=value['consequence']==current['consequence']
    return dict(valid=True,prediction=value,error=None,category=cat,old_exact=pair==(1,1),new_exact=pair==(1,-1),zero_exact=pair==(1,0),
        next_state_correct=ns,consequence_correct=co,current_exact=ns and co)

def cell(rows):
    keys=('valid','old_exact','new_exact','zero_exact','next_state_correct','consequence_correct','current_exact')
    return dict(calls=len(rows),**{k:sum(r['scoring'][k] for r in rows) for k in keys},
        categories={k:sum(r['scoring']['category']==k for r in rows) for k in ('old','zero','new','other_valid','invalid')},
        next_state_counts=dict(sorted(Counter(str(r['scoring']['prediction']['next_state']) if r['scoring']['valid'] else 'invalid' for r in rows).items())),
        consequence_counts=dict(sorted(Counter(str(r['scoring']['prediction']['consequence']) if r['scoring']['valid'] else 'invalid' for r in rows).items())))

def path_kind(values):
    if 'invalid' in values:return 'invalid_path'
    if any(values[i]=='new' and 'old' in values[i+1:] for i in range(2)):return 'new_then_old'
    if values[0]=='old' and values[1]=='new':return 'old_to_new_at_P1'
    if values[0]=='old' and values[2]=='new':return 'old_to_new_at_P2'
    if values==['old']*3:return 'old_throughout'
    return 'other_valid_path'

def trajectories(rows):
    out=[]
    for family in ('O1','O2'):
        for j in range(12):
            rs=[r for r in rows if r['descriptor']['family']==family and r['descriptor']['schedule']==j]
            scores={a:{s:next(r['scoring'] for r in rs if r['descriptor']['arm']==a and r['descriptor']['stage']==s) for s in STAGES} for a in ARMS}
            control,changed=scores['CONTROL']['P2'],scores['CHANGED']['P2']
            cp=[scores['CHANGED'][s]['category'] for s in STAGES]
            latency='excluded_no_old_P0' if cp[0]!='old' else 'P1' if cp[1]=='new' else 'P2' if cp[2]=='new' else 'no_observed_revision'
            out.append(dict(family=family,schedule=j,mapping_index=j%6,mapping=rs[0]['descriptor']['mapping'],seed=92001+j,
                target_alias=next(k for k,v in rs[0]['descriptor']['mapping'].items() if v=='ADVANCE'),conditions=scores,
                paths={a:[scores[a][s]['category'] for s in STAGES] for a in ARMS},
                path_classes={a:path_kind([scores[a][s]['category'] for s in STAGES]) for a in ARMS},latency=latency,
                P2_favorable=control['old_exact'] and changed['new_exact'],P2_reverse=control['new_exact'] and changed['old_exact']))
    return out

def criteria(cells,pairs,complete,valid,integrity,replay):
    return dict(CHANGED_P0_old_at_least_10=cells['CHANGED/P0']['old_exact']>=10,
        CHANGED_P2_new_at_least_9=cells['CHANGED/P2']['new_exact']>=9,CONTROL_P2_old_at_least_9=cells['CONTROL/P2']['old_exact']>=9,
        P2_favorable_at_least_8=pairs['favorable']>=8,P2_reverse_at_most_1=pairs['reverse']<=1,
        all_144_complete=complete,all_144_valid=valid,changed_histories_authentic=integrity,old_records_present_unchanged=integrity,
        new_records_present_unchanged=integrity,framework_source_provenance_integrity=integrity,exact_replay=replay)

def summarize(rows,replay=None):
    ts=trajectories(rows);families={};complete=len(rows)==144;valid=complete and all(r['scoring']['valid'] for r in rows)
    for f in ('O1','O2'):
        fr=[r for r in rows if r['descriptor']['family']==f];ft=[t for t in ts if t['family']==f]
        cells={a+'/'+s:cell([r for r in fr if r['descriptor']['arm']==a and r['descriptor']['stage']==s]) for a in ARMS for s in STAGES}
        pairs=dict(favorable=sum(t['P2_favorable'] for t in ft),reverse=sum(t['P2_reverse'] for t in ft))
        gates=criteria(cells,pairs,complete,valid,True,replay);supported=all(v is True for v in gates.values())
        aliases={a:{arm+'/'+st:cell([r for r in fr if r['descriptor']['arm']==arm and r['descriptor']['stage']==st and next(k for k,v in r['descriptor']['mapping'].items() if v=='ADVANCE')==a]) for arm in ARMS for st in STAGES} for a in sorted({t['target_alias'] for t in ft})}
        families[f]=dict(cells=cells,P2_pairs=pairs,criteria=gates,supported=supported,
            decision='CROSS-EPISODE STALE-MEMORY MAP REVISION '+('SUPPORTED' if supported else 'NOT ESTABLISHED'),
            revision_latency=dict(Counter(t['latency'] for t in ft)),trajectory_classes={a:dict(Counter(t['path_classes'][a] for t in ft)) for a in ARMS},by_target_alias=aliases)
    return dict(study='cross-episode-stale-memory-map-revision-v1',completed_calls=len(rows),valid_responses=sum(r['scoring']['valid'] for r in rows),
        Map_calls=len(rows),Explorer_calls=0,Recovery_model_calls=0,measured_world_executions=0,measured_Memory_commits=0,
        deterministic_setup_events=sum(3+2*r['descriptor']['stage_index'] for r in rows),
        native_fixture_Recovery_calls=sum(r['intent']['audit']['native_state_Recovery_calls'] for r in rows),
        families=families,trajectories=ts,status='FINAL' if replay is True else 'AWAITING_EXACT_REPLAY_AND_PRESERVATION',
        classification='CROSS-EPISODE STALE-MEMORY MAP REVISION '+('REPLICATED' if all(f['supported'] for f in families.values()) else 'NOT ESTABLISHED'))
