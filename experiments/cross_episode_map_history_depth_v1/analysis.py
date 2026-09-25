"""Frozen exact-pair primary rule; all depth contrasts and components reported."""
from collections import Counter
from experiments.model_map_proposal_v0.adapter import parse
DEPTHS=('D0','D1','D2')
COMPARISONS=(('D1','D0'),('D2','D0'),('D2','D1'))

def score(raw,receipt):
    try:value=parse(raw)
    except (ValueError,TypeError) as exc:return dict(valid=False,prediction=None,error=str(exc),next_state=False,consequence=False,exact=False)
    ns=value['next_state']==receipt.next_state;co=value['consequence']==receipt.realized_consequence
    return dict(valid=True,prediction=value,error=None,next_state=ns,consequence=co,exact=ns and co)

def triple(d,rows):
    scores={r['condition']:r['scoring'] for r in rows}
    contrasts={}
    for high,low in COMPARISONS:
        h,l=scores[high]['exact'],scores[low]['exact']
        contrasts[high+'_vs_'+low]=dict(favorable=h and not l,reverse=not h and l,both_exact=h and l,both_wrong=not h and not l)
    return dict(context_index=d['index'],family=d['family'],mapping_index=d['mapping_index'],mapping=d['mapping'],seed=d['seed'],
        conditions=scores,comparisons=contrasts,trajectory=' -> '.join('exact' if scores[k]['exact'] else 'wrong' for k in DEPTHS))

def aggregate(triples):
    return dict(contexts=len(triples),conditions={c:{k:sum(t['conditions'][c][k] for t in triples) for k in ('valid','exact','next_state','consequence')} for c in DEPTHS},
        comparisons={h+'_vs_'+l:{k:sum(t['comparisons'][h+'_vs_'+l][k] for t in triples) for k in ('favorable','reverse','both_exact','both_wrong')} for h,l in COMPARISONS},
        trajectory_counts=dict(sorted(Counter(t['trajectory'] for t in triples).items())))

def criteria(m,complete,integrity,replay):
    c=m['conditions'];p=m['comparisons']['D2_vs_D0'];f=m['families']
    return dict(all_36_complete=complete,D0_valid_at_least_11=c['D0']['valid']>=11,D1_valid_at_least_11=c['D1']['valid']>=11,
        D2_valid_at_least_11=c['D2']['valid']>=11,D2_exact_at_least_9=c['D2']['exact']>=9,D2_exact_exceeds_D0=c['D2']['exact']>c['D0']['exact'],
        favorable_at_least_5=p['favorable']>=5,reverse_at_most_1=p['reverse']<=1,
        O1_favorable_exceeds_reverse=f['O1']['comparisons']['D2_vs_D0']['favorable']>f['O1']['comparisons']['D2_vs_D0']['reverse'],
        O2_favorable_exceeds_reverse=f['O2']['comparisons']['D2_vs_D0']['favorable']>f['O2']['comparisons']['D2_vs_D0']['reverse'],
        system_provenance_integrity=integrity,exact_replay=replay)

def decision(gates):return 'TWO-OBSERVATION CROSS-EPISODE MAP EFFECT '+('SUPPORTED' if all(v is True for v in gates.values()) else 'NOT ESTABLISHED')

def summarize(triples,rows):
    m=aggregate(triples);m['families']={f:aggregate([t for t in triples if t['family']==f]) for f in ('O1','O2')}
    m.update(study='cross-episode-map-history-depth-v1',completed_calls=len(rows),Map_calls=len(rows),Explorer_calls=0,Recovery_calls=0,
        setup_world_executions=48,model_probe_world_executions=0,model_probe_memory_commits=0,reset_realized_events=0,
        aggregate_exact_monotone=m['conditions']['D0']['exact']<=m['conditions']['D1']['exact']<=m['conditions']['D2']['exact'],
        monotonicity_is_descriptive=True,status='AWAITING_EXACT_REPLAY_AND_PRESERVATION')
    m['criteria']=criteria(m,len(rows)==36,True,None);m['classification']=decision(m['criteria'])
    return m
