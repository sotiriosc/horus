"""Frozen role-specific thresholds; malformed proposals remain failures."""
from experiments.model_explorer_semantic_prior_study_v0.adapter import parse_surface
from experiments.model_map_proposal_v0.adapter import parse

def score(role,raw,mapping,receipt):
    if role=='Explorer':
        surface,action,error=parse_surface(raw,dict(surface_option_order=list(mapping),surface_to_underlying=mapping))
        return dict(valid=error is None,surface=surface,action=action,error=error,advance=action=='ADVANCE')
    try:value=parse(raw)
    except (ValueError,TypeError) as exc:return dict(valid=False,prediction=None,error=str(exc),next_state=False,consequence=False,exact=False)
    ns=value['next_state']==receipt.next_state;co=value['consequence']==receipt.realized_consequence
    return dict(valid=True,prediction=value,error=None,next_state=ns,consequence=co,exact=ns and co)

def pair(d,role,rows):
    s={r['condition']:r['scoring'] for r in rows};c,f=s['CARRY'],s['FRESH'];key='advance' if role=='Explorer' else 'exact'
    return dict(context_index=d['index'],family=d['family'],mapping_index=d['mapping_index'],mapping=d['mapping'],role=role,
        conditions=s,favorable=c[key] and not f[key],reverse=not c[key] and f[key],both_positive=c[key] and f[key],
        both_negative=not c[key] and not f[key],identical_valid_choices=(c['valid'] and f['valid'] and c.get('action')==f.get('action')) if role=='Explorer' else None)

def aggregate(pairs,role):
    keys=['valid','advance'] if role=='Explorer' else ['valid','next_state','consequence','exact']
    result=dict(pairs=len(pairs),conditions={c:{k:sum(p['conditions'][c][k] for p in pairs) for k in keys} for c in ('CARRY','FRESH')})
    result.update({k:sum(p[k] for p in pairs) for k in ('favorable','reverse','both_positive','both_negative')})
    if role=='Explorer':
        result['identical_valid_choices']=sum(p['identical_valid_choices'] for p in pairs)
        result['actions']={c:{a:sum(p['conditions'][c]['action']==a for p in pairs) for a in ('ADVANCE','HOLD','RETREAT',None)} for c in ('CARRY','FRESH')}
        result['actions']={c:{('INVALID' if a is None else a):v for a,v in counts.items()} for c,counts in result['actions'].items()}
    return result

def criteria(role,m,complete):
    c,f=m['conditions']['CARRY'],m['conditions']['FRESH'];o=m['families']
    common=dict(all_24_complete=complete,carry_valid_at_least_11=c['valid']>=11,fresh_valid_at_least_11=f['valid']>=11)
    if role=='Explorer':return {**common,'carry_advance_at_least_9':c['advance']>=9,'favorable_at_least_5':m['favorable']>=5,
        'reverse_at_most_1':m['reverse']<=1,'O1_carry_advance_at_least_4':o['O1']['conditions']['CARRY']['advance']>=4,
        'O2_carry_advance_at_least_4':o['O2']['conditions']['CARRY']['advance']>=4}
    return {**common,'carry_exact_exceeds_fresh':c['exact']>f['exact'],'favorable_at_least_4':m['favorable']>=4,
        'reverse_at_most_1':m['reverse']<=1,'O1_favorable_exceeds_reverse':o['O1']['favorable']>o['O1']['reverse'],
        'O2_favorable_exceeds_reverse':o['O2']['favorable']>o['O2']['reverse']}

def summarize(pairs,rows):
    out={}
    for role in ('Explorer','Map'):
        ps=[p for p in pairs if p['role']==role];m=aggregate(ps,role)
        m['families']={f:aggregate([p for p in ps if p['family']==f],role) for f in ('O1','O2')}
        m['criteria']=criteria(role,m,sum(r['role']==role for r in rows)==24)
        m['supported']=all(m['criteria'].values())
        m['decision']=f'CROSS-EPISODE {role.upper()} MEMORY EFFECT '+('SUPPORTED' if m['supported'] else 'NOT ESTABLISHED')
        out[role]=m
    return dict(study='cross-episode-model-transfer-v0',completed_calls=len(rows),roles=out,
        threshold_decision='CROSS-EPISODE AUTHENTICATED-MEMORY BEHAVIORAL TRANSFER '+('SUPPORTED' if all(m['supported'] for m in out.values()) else 'NOT ESTABLISHED'),
        status='AWAITING_EXACT_REPLAY_AND_PRESERVATION',model_probe_world_executions=0,model_probe_memory_commits=0,
        setup_world_executions=48,reset_realized_events=0,Recovery_calls=0)
