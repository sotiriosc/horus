"""Inactive, pure Phase 3 candidate: BOUNDED_EMPIRICAL_EVIDENCE_ACQUISITION.

The caller must supply the complete, chronological pre-decision event projection
AFTER the existing protected receipt/authorization/Memory replay has verified it.
This function checks projection consistency; it does not authenticate signatures,
issue receipts, execute actions, call a model, or modify grounded state.
"""

from re import fullmatch

NAME = 'BOUNDED_EMPIRICAL_EVIDENCE_ACQUISITION'
SHORT_ID = 'E'
SOURCE = 'EMPIRICAL_EVIDENCE_ACQUISITION'
TRIGGER_REASON = 'DETERIORATED_EMPIRICAL_RELATION_WITH_MISSING_EVIDENCE'
WINDOW = 4  # frozen grounded_state.empirical.WINDOW; no fitted threshold
ACTIONS = ('ADVANCE', 'HOLD', 'RETREAT')
EMPIRICAL_KINDS = ('EMPIRICALLY_STABLE', 'VARIABLE_RELATION')


def _consequence(value):
    if type(value) is not int or value not in (-1, 0, 1):
        raise ValueError('invalid realized consequence')
    return value


def _outcome(value):
    if not isinstance(value, dict) or type(value.get('next_state')) is not int:
        raise ValueError('invalid observed next state')
    return (value['next_state'], _consequence(value.get('consequence')))


def empirical_component(assessment, observed_outcomes):
    """Exact H2 empirical signal, using only this relation's prior observations.

    This component is also usable on relation-only control traces; it does not
    assert that an unseen alternative or an admissible action set exists there.
    """
    if not isinstance(assessment, dict) or not isinstance(observed_outcomes, (list, tuple)):
        raise ValueError('invalid empirical input')
    observed = tuple(_outcome(x) for x in observed_outcomes)
    recent = tuple(_outcome(x) for x in assessment.get('recent_window', ()))
    if type(assessment.get('observation_count')) is not int or assessment['observation_count'] != len(observed):
        raise ValueError('grounded count disagrees with verified history')
    if recent != observed[-WINDOW:]:
        raise ValueError('grounded recent window disagrees with verified history')
    recent_sum = sum(x[1] for x in recent)
    cumulative_sum = sum(x[1] for x in observed)
    kind = assessment.get('kind')
    signal = (kind in EMPIRICAL_KINDS and assessment.get('possible_change') is None
              and len(recent) == WINDOW and recent_sum <= 0 and cumulative_sum <= 0)
    return dict(signal=signal, recent_sum=recent_sum, cumulative_sum=cumulative_sum,
                observation_count=len(observed), empirical_kind=kind)


def _checked_history(history):
    if not isinstance(history, (list, tuple)):
        raise ValueError('history must be a complete ordered event sequence')
    for expected_sequence, event in enumerate(history, 1):
        if not isinstance(event, dict) or event.get('event_stream_sequence') != expected_sequence:
            raise ValueError('history has an omitted, duplicated, or unordered event')
        if event.get('authorization_status') != 'AUTHORIZED':
            continue  # a non-authorized event remains in the sequence and breaks the suffix
        if (not event.get('event_identity') or not event.get('receipt_identity')
                or not isinstance(event.get('receipt_sha256'), str)
                or fullmatch(r'[0-9a-f]{64}', event['receipt_sha256']) is None
                or type(event.get('state')) is not int
                or type(event.get('next_state')) is not int
                or event.get('action') not in ACTIONS):
            raise ValueError('authorized event lacks verified projection fields')
        _consequence(event.get('consequence'))
    return history


def evaluate(current_state, admissible_actions, assessments, history):
    """Return a prospective recommendation; never select/execute an actual action.

    `history` includes every pre-decision event in order, including non-authorized
    events, and is supplied by the existing authenticated replay boundary.
    Invalid/incomplete projections raise ValueError, so no acquisition is returned.
    """
    if type(current_state) is not int:
        raise ValueError('invalid current state')
    if (not isinstance(admissible_actions, (list, tuple)) or
            not admissible_actions or len(set(admissible_actions)) != len(admissible_actions) or
            any(a not in ACTIONS for a in admissible_actions)):
        raise ValueError('invalid admissible action set')
    if not isinstance(assessments, dict) or any(a not in assessments for a in admissible_actions):
        raise ValueError('missing grounded assessment')
    _checked_history(history)

    last = history[-1] if history else None
    repeated_action = (last.get('action') if last and
                       last.get('authorization_status') == 'AUTHORIZED' else None)
    relation = ([current_state, repeated_action] if repeated_action else None)
    suffix = []
    if repeated_action in admissible_actions:
        for event in reversed(history):
            if (event.get('authorization_status') != 'AUTHORIZED' or
                    event.get('state') != current_state or
                    event.get('next_state') != current_state or
                    event.get('action') != repeated_action):
                break
            suffix.append(event)
    suffix.reverse()
    count = len(suffix)

    base = dict(candidate=NAME, short_id=SHORT_ID, eligible=False,
                target_action=None, source=None, reason='NO_TRIGGER',
                qualifying_relation=relation, suffix_count=count,
                recent_sum=None, cumulative_sum=None, unseen_candidates=[])
    if count < WINDOW:
        return base

    selected = assessments[repeated_action]
    if (not isinstance(selected, dict) or selected.get('relation_type') != 'EMPIRICAL' or
            selected.get('kind') not in EMPIRICAL_KINDS or
            selected.get('possible_change') is not None or
            selected.get('relation') != f'{current_state}:{repeated_action}'):
        return base

    all_observed = [dict(next_state=e['next_state'], consequence=e['consequence'])
                    for e in history if e.get('authorization_status') == 'AUTHORIZED' and
                    e.get('state') == current_state and e.get('action') == repeated_action]
    empirical = empirical_component(selected, all_observed)
    base['recent_sum'] = empirical['recent_sum']
    base['cumulative_sum'] = empirical['cumulative_sum']
    if not empirical['signal']:
        return base
    if tuple(_outcome(x) for x in all_observed[-WINDOW:]) != tuple(
            (e['next_state'], e['consequence']) for e in suffix[-WINDOW:]):
        raise ValueError('recent relation observations disagree with consecutive suffix')

    for action in admissible_actions:
        assessment = assessments[action]
        if not isinstance(assessment, dict) or assessment.get('relation') != f'{current_state}:{action}':
            raise ValueError('assessment does not match current relation')
        if (assessment.get('relation_type') == 'DETERMINISTIC' and
                assessment.get('kind') == 'ESTABLISHED' and
                isinstance(assessment.get('established_value'), dict) and
                assessment['established_value'].get('consequence') == 1):
            return base

    unseen = [action for action in ACTIONS if action in admissible_actions and
              action != repeated_action and assessments[action].get('kind') == 'UNSEEN' and
              assessments[action].get('observation_count') == 0]
    base['unseen_candidates'] = unseen
    if not unseen:
        return base
    return {**base, 'eligible': True, 'target_action': unseen[0],
            'source': SOURCE, 'reason': TRIGGER_REASON}
