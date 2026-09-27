"""Frozen separate-family criteria; invalids remain in all denominators."""
from collections import Counter
from experiments.model_explorer_semantic_prior_study_v0.adapter import parse_surface
STAGES=('P0','P1','P2');ARMS=('CONTROL','CHANGED');ACTIONS=('HOLD','RETREAT','ADVANCE','invalid')

def score(raw,mapping,current_best):
    surface,action,error=parse_surface(raw,dict(surface_option_order=list(mapping),surface_to_underlying=mapping))
    return dict(valid=action is not None,surface=surface,action=action,error=error,category=action or 'invalid',
        old=action=='HOLD',new=action=='RETREAT',current_best=action==current_best)

def cell(rows):
    return dict(calls=len(rows),valid=sum(r['scoring']['valid'] for r in rows),
        counts={k:sum(r['scoring']['category']==k for r in rows) for k in ACTIONS},
        current_best=sum(r['scoring']['current_best'] for r in rows))

def path_kind(v):
    if 'invalid' in v:return 'invalid_path'
    if any(v[i]=='RETREAT' and 'HOLD' in v[i+1:] for i in range(2)):return 'RETREAT_then_HOLD'
    if v[0]=='HOLD' and v[1]=='RETREAT':return 'HOLD_to_RETREAT_at_P1'
    if v[0]=='HOLD' and v[2]=='RETREAT':return 'HOLD_to_RETREAT_at_P2'
    if v==['HOLD']*3:return 'HOLD_throughout'
    return 'other'

def trajectories(rows):
    out=[]
    for f in ('O1','O2'):
        for j in range(12):
            rs=[r for r in rows if r['descriptor']['family']==f and r['descriptor']['schedule']==j]
            scores={a:{s:next(r['scoring'] for r in rs if r['descriptor']['arm']==a and r['descriptor']['stage']==s) for s in STAGES} for a in ARMS}
            paths={a:[scores[a][s]['category'] for s in STAGES] for a in ARMS};cp=paths['CHANGED']
            latency='excluded_no_HOLD_P0' if cp[0]!='HOLD' else 'P1' if cp[1]=='RETREAT' else 'P2' if cp[2]=='RETREAT' else 'never'
            out.append(dict(family=f,schedule=j,mapping_index=j%6,mapping=rs[0]['descriptor']['mapping'],seed=93001+j,
                conditions=scores,paths=paths,path_classes={a:path_kind(v) for a,v in paths.items()},latency=latency,
                P2_favorable=paths['CONTROL'][2]=='HOLD' and cp[2]=='RETREAT',P2_reverse=paths['CONTROL'][2]=='RETREAT' and cp[2]=='HOLD'))
    return out

def validity_gate(total,cell_validities):return total>=140 and all(v>=11 for v in cell_validities)

def criteria(cells,pairs,complete,valid,integrity,replay):
    return dict(CHANGED_P0_HOLD_at_least_10=cells['CHANGED/P0']['counts']['HOLD']>=10,
        CHANGED_P2_RETREAT_at_least_9=cells['CHANGED/P2']['counts']['RETREAT']>=9,
        CONTROL_P2_HOLD_at_least_9=cells['CONTROL/P2']['counts']['HOLD']>=9,
        P2_favorable_at_least_8=pairs['favorable']>=8,P2_reverse_at_most_1=pairs['reverse']<=1,
        all_144_complete=complete,global_and_cell_validity=valid,histories_authentic=integrity,
        old_records_present_unchanged=integrity,new_records_present_unchanged=integrity,framework_provenance_integrity=integrity,exact_replay=replay)

def summarize(rows,replay=None):
    ts=trajectories(rows);families={};total=sum(r['scoring']['valid'] for r in rows)
    all_cells={f:{a+'/'+s:cell([r for r in rows if r['descriptor']['family']==f and r['descriptor']['arm']==a and r['descriptor']['stage']==s]) for a in ARMS for s in STAGES} for f in ('O1','O2')}
    valid=validity_gate(total,[c['valid'] for cells in all_cells.values() for c in cells.values()])
    for f,cells in all_cells.items():
        fr=[r for r in rows if r['descriptor']['family']==f];ft=[t for t in ts if t['family']==f]
        pairs=dict(favorable=sum(t['P2_favorable'] for t in ft),reverse=sum(t['P2_reverse'] for t in ft))
        integrity=all(r['intent']['audit']['passed'] and r['intent']['audit']['old_records_present_unchanged'] and r['intent']['audit']['new_records_present_unchanged'] for r in rows)
        gates=criteria(cells,pairs,len(rows)==144,valid,integrity,replay);supported=all(v is True for v in gates.values())
        aliases={alias:{a+'/'+s:cell([r for r in fr if r['descriptor']['mapping'][alias]=='HOLD' and r['descriptor']['arm']==a and r['descriptor']['stage']==s]) for a in ARMS for s in STAGES} for alias in fr[0]['descriptor']['mapping']}
        families[f]=dict(cells=cells,P2_pairs=pairs,criteria=gates,supported=supported,decision='CROSS-EPISODE STALE-MEMORY EXPLORER REVISION '+('SUPPORTED' if supported else 'NOT ESTABLISHED'),
            revision_latency=dict(Counter(t['latency'] for t in ft)),trajectory_classes={a:dict(Counter(t['path_classes'][a] for t in ft)) for a in ARMS},by_HOLD_alias=aliases)
    return dict(study='cross-episode-stale-memory-explorer-revision-v1',completed_calls=len(rows),valid_responses=total,
        Explorer_calls=len(rows),Map_calls=0,Recovery_model_calls=0,measured_world_executions=0,measured_Memory_commits=0,
        deterministic_setup_events=sum(6+r['descriptor']['stage_index'] for r in rows),
        native_state_Recovery_calls=sum(r['intent']['audit']['native_state_Recovery_calls'] for r in rows),
        native_measurement_Recovery_calls=sum(r['intent']['audit']['native_measurement_Recovery_calls'] for r in rows),
        families=families,trajectories=ts,status='FINAL' if replay is True else 'AWAITING_EXACT_REPLAY_AND_PRESERVATION',
        classification='CROSS-EPISODE STALE-MEMORY EXPLORER REVISION '+('REPLICATED' if all(f['supported'] for f in families.values()) else 'NOT ESTABLISHED'))
