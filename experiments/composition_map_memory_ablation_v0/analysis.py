"""Frozen paired scoring. A malformed proposal is invalid and never correct."""
from collections import Counter
from experiments.model_map_proposal_v0.adapter import parse


def score(raw,receipt):
    try:
        prediction=parse(raw); error=None
    except ValueError as exc:
        prediction=None; error=str(exc)
    valid=prediction is not None
    state=valid and prediction['next_state']==receipt['next_state']
    consequence=valid and prediction['consequence']==receipt['realized_consequence']
    return dict(prediction=prediction,parse_error=error,valid=valid,next_state=state,consequence=consequence,exact=state and consequence)


def pair(context,rows):
    h,w=(next(r['scoring'] for r in rows if r['condition']==k) for k in ('H','W'))
    if not h['valid'] or not w['valid']:change='invalid_prediction_present'
    else:
        state=h['prediction']['next_state']!=w['prediction']['next_state']
        consequence=h['prediction']['consequence']!=w['prediction']['consequence']
        change='both_changed' if state and consequence else 'state_changed_only' if state else 'consequence_changed_only' if consequence else 'identical'
    direction=('exact_to_same_exact' if w['exact'] else 'wrong_to_exact') if h['exact'] else 'exact_to_wrong' if w['exact'] else 'wrong_to_same_wrong' if h['prediction']==w['prediction'] else 'wrong_to_different_wrong'
    return dict(context_index=context['index'],episode=context['episode'],decision=context['decision'],family=context['family'],
        depth=context['depth'],state=context['state'],action=context['action'],alias=context['alias'],
        H=h,W=w,output_change=change,visibility_W_to_H=direction,receipt_sha256=context['receipt_sha256'])


def summarize(pairs):
    totals={k:{field:sum(p[k][field] for p in pairs) for field in ('valid','next_state','consequence','exact')} for k in ('H','W')}
    effects={}
    for field in ('next_state','consequence','exact'):
        favorable=sum(p['H'][field] and not p['W'][field] for p in pairs)
        reverse=sum(p['W'][field] and not p['H'][field] for p in pairs)
        effects[field]=dict(favorable=favorable,reverse=reverse,both_correct=sum(p['H'][field] and p['W'][field] for p in pairs),both_wrong=sum(not p['H'][field] and not p['W'][field] for p in pairs),net=favorable-reverse)
    return dict(contexts=len(pairs),conditions=totals,effects=effects,output_changes=dict(Counter(p['output_change'] for p in pairs)),visibility_W_to_H=dict(Counter(p['visibility_W_to_H'] for p in pairs)))


def metrics(pairs):
    result=summarize(pairs)
    for field in ('family','depth','state','action','alias'):
        group = lambda p: ('3+' if p['depth']>=3 else str(p['depth'])) if field=='depth' else str(p[field])
        result['by_'+field]={key:summarize([p for p in pairs if group(p)==key]) for key in sorted({group(p) for p in pairs})}
    result['by_condition_order']={k:summarize([p for p in pairs if ('H_first' if p['context_index']%2==0 else 'W_first')==k]) for k in ('H_first','W_first')}
    return result


def criteria(result,calls_complete,preservation,integrity,replay):
    c=result['conditions']; e=result['effects']['exact']
    return dict(all_84_complete=calls_complete,H_valid_at_least_40=c['H']['valid']>=40,W_valid_at_least_40=c['W']['valid']>=40,
        favorable_minus_reverse_at_least_10=e['net']>=10,
        O1_favorable_exceeds_reverse=result['by_family']['O1']['effects']['exact']['net']>0,
        O2_favorable_exceeds_reverse=result['by_family']['O2']['effects']['exact']['net']>0,
        H_exact_exceeds_W=c['H']['exact']>c['W']['exact'],historical_memory_receipts_unchanged=preservation,
        parser_model_sampler_integrity=integrity,exact_recorded_response_replay=replay)
