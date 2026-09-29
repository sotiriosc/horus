"""Explicitly approved grounded authority + exact S + exact E selector."""
from experiments.grounded_stagnation_escape_promotion_controlled_v0 import worker as incumbent
from experiments.empirical_evidence_acquisition_proposal_v0 import candidate as empirical
from .empirical_adapter import authenticated_projection, recommendation, IntegrationInvariantError


def integrated_decide(store, memory, client, index):
    # Verify before constructing the incumbent context; never heal partial input.
    history = authenticated_projection(store, memory)
    context = incumbent.context(store, memory, index)
    if context['route']['route'] == 'MECHANICAL':
        return incumbent.canonical_action_decision(store, client, index, context)
    s_action, suffix = incumbent.escape_choice(store, memory, context['state'], context['assessments'])
    if suffix != context['suffix']:
        raise IntegrationInvariantError('S suffix changed during integration')
    e = recommendation(context, history)
    if s_action is not None and e['eligible']:
        raise IntegrationInvariantError('S and E simultaneously eligible')
    if s_action is not None:
        return incumbent.frozen_decide(store, memory, client, 'ACTIVE', 'S', index, context)
    if not e['eligible']:
        return incumbent.canonical_action_decision(store, client, index, context)
    action = e['target_action']
    if (action not in context['candidate_set'] or e['source'] != empirical.SOURCE or
            e['reason'] != empirical.TRIGGER_REASON):
        raise IntegrationInvariantError('invalid E recommendation binding')
    route = {**context['route'], 'route': empirical.SOURCE,
             'source': empirical.SOURCE, 'action': action, 'reason': empirical.TRIGGER_REASON}
    info = dict(call_id=None, raw_output_sha256=None, request_sha256=None,
        context_tokens=0, output_tokens=0, latency_seconds=0, status='NOT_CALLED')
    store.append('calls', 'ACTION_FROZEN', dict(decision_id=f'C:D{index:02d}',
        selected_action=action, decision_source=empirical.SOURCE, reason=empirical.TRIGGER_REASON,
        action_call_id=None, raw_output_sha256=None, candidate=e))
    store.save(state=context['state'], next_transaction_id=store.checkpoint['next_transaction_id'])
    # Preserve the incumbent six-value execution interface and S suffix shape.
    return action, empirical.SOURCE, route, info, context['assessments'], context['suffix']
