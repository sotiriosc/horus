"""Two independent frozen decisions; R1/R2 remain descriptive controls."""
from collections import Counter
from .protocol import RELATIONS,CONDITIONS,ACTIONS

def cell(rows):
    return dict(calls=len(rows),valid=sum(r['scoring']['valid'] for r in rows),correct=sum(r['scoring']['correct'] for r in rows),
        actions=dict(Counter(r['scoring']['selected_action'] or 'INVALID' for r in rows)),aliases=dict(Counter(r['scoring']['selected_alias'] or 'INVALID' for r in rows)))
def summarize(rows,replay=None):
    pairs=[];families={}
    for f in ('O1','O2'):
        fr=[r for r in rows if r['descriptor']['family']==f];fp=[];relations={}
        for relation in RELATIONS:
            rr=[r for r in fr if r['descriptor']['relation']==relation]
            for j in range(12):
                matched={r['descriptor']['condition']:r for r in rr if r['descriptor']['schedule']==j}
                if set(matched)!=set(CONDITIONS):continue
                n,v=[matched[c]['scoring'] for c in CONDITIONS];d=matched['N']['descriptor'];comparable=n['valid'] and v['valid']
                fp.append(dict(family=f,relation=relation,schedule=j,mapping_index=j%6,mapping=d['mapping'],seed=d['seed'],
                    true_best=n['true_best'],true_best_alias=n['true_best_alias'],N=n,V=v,
                    same=comparable and n['selected_action']==v['selected_action'],different=comparable and n['selected_action']!=v['selected_action'],not_comparable=not comparable))
            rp=[p for p in fp if p['relation']==relation]
            relations[relation]=dict(N=cell([r for r in rr if r['descriptor']['condition']=='N']),V=cell([r for r in rr if r['descriptor']['condition']=='V']),
                same=sum(p['same'] for p in rp),different=sum(p['different'] for p in rp),not_comparable=sum(p['not_comparable'] for p in rp),
                N_by_target={a:cell([r for r in rr if r['descriptor']['condition']=='N' and r['scoring']['true_best']==a]) for a in ACTIONS})
        r3=relations['R3'];r3rows=[r for r in fr if r['descriptor']['relation']=='R3']
        primary=dict(all_24_R3_complete=len(r3rows)==24,valid_at_least_23=sum(r['scoring']['valid'] for r in r3rows)>=23,
            N_best_at_least_10=r3['N']['correct']>=10,V_best_at_least_10=r3['V']['correct']>=10,same_at_least_10=r3['same']>=10,
            every_N_target_at_least_3_of_4=all(c['calls']==4 and c['correct']>=3 for c in r3['N_by_target'].values()),exact_replay=replay)
        nc=sum(relations[r]['N']['correct'] for r in RELATIONS);vc=sum(relations[r]['V']['correct'] for r in RELATIONS)
        invariance=dict(all_72_complete=len(fr)==72,valid_at_least_70=sum(r['scoring']['valid'] for r in fr)>=70,same_at_least_32=sum(p['same'] for p in fp)>=32,
            accuracy_difference_at_most_3=abs(nc-vc)<=3,R3_same_at_least_10=r3['same']>=10,exact_replay=replay)
        supported=lambda g:all(v is True for v in g.values())
        families[f]=dict(relations=relations,primary=dict(criteria=primary,supported=supported(primary),decision='ZERO-OVER-NEGATIVE COMPARATOR '+('SUPPORTED' if supported(primary) else 'NOT ESTABLISHED')),
            next_state=dict(criteria=invariance,supported=supported(invariance),decision='NEXT_STATE IRRELEVANCE '+('SUPPORTED' if supported(invariance) else 'NOT ESTABLISHED'),
                same=sum(p['same'] for p in fp),different=sum(p['different'] for p in fp),not_comparable=sum(p['not_comparable'] for p in fp),N_correct=nc,V_correct=vc,accuracy_difference=abs(nc-vc)),
            by_relation_mapping={rel:{str(j):{c:cell([r for r in fr if r['descriptor']['relation']==rel and r['descriptor']['mapping_index']==j and r['descriptor']['condition']==c]) for c in CONDITIONS} for j in range(6)} for rel in RELATIONS},
            by_relation_target={rel:{a:{c:cell([r for r in fr if r['descriptor']['relation']==rel and r['scoring']['true_best']==a and r['descriptor']['condition']==c]) for c in CONDITIONS} for a in ACTIONS} for rel in RELATIONS},
            by_relation_target_alias={rel:{a:{c:cell([r for r in fr if r['descriptor']['relation']==rel and r['scoring']['true_best_alias']==a and r['descriptor']['condition']==c]) for c in CONDITIONS} for a in next(r['descriptor']['mapping'] for r in fr)} for rel in RELATIONS})
        pairs+=fp
    return dict(study='explorer-finite-value-comparator-v0',completed_calls=len(rows),Explorer_calls=len(rows),Map_calls=0,Recovery_model_calls=0,
        world_executions=0,Memory_changes=0,valid_responses=sum(r['scoring']['valid'] for r in rows),families=families,pairs=pairs,
        calls=[dict(descriptor=r['descriptor'],scoring=r['scoring']) for r in rows],
        classification='ZERO-OVER-NEGATIVE COMPARATOR '+('REPLICATED' if all(f['primary']['supported'] for f in families.values()) else 'NOT ESTABLISHED'),
        next_state_classification='NEXT_STATE IRRELEVANCE '+('REPLICATED' if all(f['next_state']['supported'] for f in families.values()) else 'NOT ESTABLISHED'),
        control_scope='R1/R2 descriptive only; no frozen pass criterion or rescue of R3.',status='FINAL' if replay is True else 'AWAITING_EXACT_REPLAY_AND_PRESERVATION')
