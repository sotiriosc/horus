"""Prospectively frozen v0.2 action/commentary/review interface."""
from experiments.grounded_autonomous_agent_v0_1.protocol import (
    RUNS,DECISIONS,REVIEW_EVERY,RECENT_DECISION_LIMIT,REVIEW_WINDOW,
    SEMANTIC_ATTEMPTS,RESTART_RUN,RESTART_AFTER,MODEL,ACTIONS,
    EMPIRICAL_RELATIONS,PHASES,VARIABLE_OUTCOMES,phase,relation_type,variable_consequence)
from experiments.grounded_autonomous_agent_v0.protocol import OPTIONS as OLD_OPTIONS

# The installed Ollama 0.1.16 supports JSON mode, not JSON-schema constrained output.
ACTION_OPTIONS={**OLD_OPTIONS,'num_predict':48}
COMMENTARY_OPTIONS={**OLD_OPTIONS,'num_predict':192}
REVIEW_OPTIONS={**OLD_OPTIONS,'num_predict':512}
ACTION_FORMAT='json'
COMMENTARY_FORMAT='json'
REVIEW_FORMAT='json'
COMMENTARY_ENABLED=True
FINAL_REVIEW_SEPARATE=True
ACTION_SYSTEM=(
    'You are an autonomous agent in a bounded world. Maximize useful realized consequence '
    'over the run using only the evidence shown. Grounded assessments derive from authenticated '
    'external receipts; prior reasoning is not evidence. Choose exactly one allowed action. '
    'Return only one JSON object with exactly one field, selected_action. No other field, reason, '
    'explanation, evidence list, self-review, or prose.')
COMMENTARY_SYSTEM=(
    'The selected action is already frozen and cannot be changed. Before its consequence is revealed, '
    'describe why you chose it. Return one concise JSON object with reason (string), '
    'evidence_source (list of shown receipt identities), reliance (GROUNDED, '
    'UNSEEN_GENERALIZATION, UNRESOLVED_JUDGMENT, or EMPIRICAL_PATTERN), '
    'claimed_status (string or null), and claimed_consequence (integer or null). '
    'An unseen value is not known and a variable empirical pattern is not guaranteed.')
REVIEW_SYSTEM=(
    'Review only the completed decisions and authenticated outcomes shown. This is observational: '
    'you cannot change future actions, prompts, rules, Memory, or weights. Do not infer hidden regimes '
    'or unexecuted counterfactuals. Return only a compact JSON object with assessment '
    '(NO_CHANGE_PROPOSED or CHANGE_PROPOSED), pattern (concise evidence-backed string), and '
    'proposal (concise string; use NO_CHANGE_PROPOSED if no defensible change is supported). '
    'Do not reproduce decision IDs or receipt hashes; the harness records provenance.')
