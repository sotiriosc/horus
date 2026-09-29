"""Frozen grounded-authority autonomous policy and model interface."""
from experiments.grounded_autonomous_agent_v0_2.protocol import (
    RUNS, DECISIONS, REVIEW_EVERY, REVIEW_WINDOW, RECENT_DECISION_LIMIT,
    RESTART_RUN, RESTART_AFTER, MODEL, ACTIONS, ACTION_OPTIONS, ACTION_FORMAT,
    REVIEW_OPTIONS, REVIEW_FORMAT, phase, relation_type, variable_consequence)

GOAL='Maximize useful realized consequence over the run using the evidence available to you.'
CEILING=1
ACCEPTABLE_MIN=0
ACTION_SYSTEM=(
    'You are a reasoning component in a bounded world. Authenticated grounded assessments '
    'are authoritative for exact experienced deterministic relations. The admissible actions '
    'have already excluded inferior known actions. Choose one admissible action using only '
    'the shown goal, state, assessments, and bounded history. Unseen relations are unknown; '
    'empirical patterns and unresolved changes are not deterministic facts. You may explore '
    'a genuinely uncertain relation or select the best known admissible fallback. '
    'Return only a JSON object with exactly one selected_action field and no explanation.')
REVIEW_SYSTEM=(
    'Review only the five completed decisions and authenticated receipts shown. You have no '
    'authority to change Memory, policy, prompts, future choices or weights. Do not infer '
    'hidden regimes or unexecuted counterfactuals. Return only a compact JSON object: '
    'either {"assessment":"NO_CHANGE_PROPOSED"}, or {"pattern":"concise evidence-backed '
    'observation","proposal":"concise proposed behavioral change"}. Do not invent a change.')

KNOWN='ESTABLISHED'
UNCERTAIN_KINDS=('UNSEEN','UNRESOLVED_CHANGE','EMPIRICALLY_STABLE',
    'VARIABLE_RELATION','POSSIBLE_REGIME_CHANGE')

def known_value(assessment):
    if assessment['relation_type']=='DETERMINISTIC' and assessment['kind']==KNOWN:
        value=assessment['established_value']
        if not isinstance(value,dict) or type(value.get('consequence')) is not int:
            raise ValueError('invalid authenticated established value')
        return value['consequence']
    if assessment['kind'] not in UNCERTAIN_KINDS:
        raise ValueError('unregistered grounded kind: '+assessment['kind'])
    return None

def select_route(assessments):
    if set(assessments)!=set(ACTIONS):raise ValueError('assessment/action mismatch')
    values={action:known_value(assessments[action]) for action in ACTIONS}
    ceiling=[action for action in ACTIONS if values[action]==CEILING]
    if ceiling:
        return dict(route='MECHANICAL',source='GROUNDED_MECHANICAL',
            action=ceiling[0],candidates=[ceiling[0]],known_values=values,
            reason='ESTABLISHED_GLOBAL_CEILING')
    known=[action for action in ACTIONS if values[action] is not None]
    unknown=[action for action in ACTIONS if values[action] is None]
    if not unknown:
        best=max(values.values());action=next(a for a in ACTIONS if values[a]==best)
        return dict(route='MECHANICAL',source='GROUNDED_MECHANICAL',
            action=action,candidates=[action],known_values=values,
            reason='ALL_ACTIONS_ESTABLISHED')
    best_known=(None if not known else next(a for a in ACTIONS if values[a]==max(values[x] for x in known)))
    candidates=[a for a in ACTIONS if a==best_known or a in unknown]
    return dict(route='MODEL',source=None,action=None,candidates=candidates,
        known_values=values,reason='UNCERTAINTY_REMAINS')

def source_for_model_choice(route,assessments,action):
    if action not in route['candidates']:raise ValueError('action outside admissible set')
    a=assessments[action]
    if a['kind']=='UNSEEN':return 'MODEL_FOR_UNSEEN'
    if route['known_values'][action] is None:return 'MODEL_FOR_UNRESOLVED'
    return ('SAFE_GROUNDED_FALLBACK' if route['known_values'][action]>=ACCEPTABLE_MIN
            else 'MODEL_WITH_KNOWN_NEGATIVE_FALLBACK')
