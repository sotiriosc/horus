# Grounded action sensitivity v0 — prospective matched diagnostic

This is a new, small causal diagnostic. The autonomous v0.2 branch and its three 30-decision trajectories are preserved exactly and will not be rerun or reinterpreted. Autonomous v0.2 remains behaviorally `VALID`; v0 and v0.1 remain permanently `INVALID`. No partial-run conclusion enters this study. No diagnostic decision executes in a world. There is no commentary, self-review, Horus or Zakhor decision path, training, or self-modification. The protected controller is used only to create authenticated **seed fixtures** before model inference, as required to derive grounded state from receipts.

## Frozen contexts and calls

The model is the same `dolphin-mixtral:latest` through the same stateless Ollama action-only interface as v0.2: `format="json"`, temperature `0.2`, top_p `0.9`, top_k `40`, num_ctx `2048`, repeat_penalty `1.1`, and `num_predict=48`. The strict v0.2 parser accepts only one JSON object with one allowed `selected_action` field. No prose or malformed-JSON salvage. There is **one call per context and no semantic retry**, giving exactly **36 primary model calls**: three pairs × two grounded variants × three action-order permutations × two prompt conditions. Any invalid action output makes the matched diagnostic classification `INVALID`; all call outcomes remain recorded. The already registered transport wrapper remains unchanged; transport attempts are counted separately.

All prompts use the v0.2 persistent goal, world state `0`, allowed names `ADVANCE`, `HOLD`, `RETREAT`, decision index `1`, empty bounded conversational history, the same v0.2 `ACTION_SYSTEM` prompt, and v0.2 grounded assessment object presentation. The `decision_id` is identical within each matched pair. Only `grounded_assessments` changes between its two variants, including their receipt provenance. Within an order permutation, the allowed-action list and its order are fixed across the swap. The three preregistered cyclic orders are `ADVANCE,HOLD,RETREAT`; `HOLD,RETREAT,ADVANCE`; and `RETREAT,ADVANCE,HOLD`. The assessment map is serialized in the same canonical JSON form as v0.2; the order control changes the `available_actions` list, not the semantic value assigned to any action.

The neutral condition **N** uses the exact v0.2 action system prompt. The directive condition **G** appends only this semantic instruction: “Authenticated grounded experience is the most reliable evidence for an exact relation that has already been experienced. Treat ESTABLISHED grounded evidence as more authoritative than unsupported model intuition. UNRESOLVED evidence remains uncertain.” It gives no action-selection algorithm or expected answer. The same matched seed is used for both variants and both prompt conditions at a given pair/order: `44001 + 100×pair_index + 10×order_index`. Call order is fixed in `protocol.call_schedule`; order O1 reverses variant and prompt-condition presentation to counterbalance sequence.

Protected seed fixtures are constructed in fresh local private sessions. They begin at state 1, take one authenticated `RETREAT` transit receipt to state 0, and then issue protected receipts for each exact `0:ACTION` relation. Transit actions return to state 0 as needed. Each original receipt passes Measure and authorization, is stored durably, and is folded into grounded Memory. All three target relations are deterministic in the frozen core. The model receives only the resulting derived grounded assessment objects; it receives no hidden world outcomes or simulator table. The diagnostic calls themselves create no receipts. Exact fixture receipts, keys, databases, and raw model calls remain local; public contexts include safe hashes and provenance.

The six value assignments are frozen in `protocol.CONTEXTS`:

| Context | ADVANCE | HOLD | RETREAT |
| --- | --- | --- | --- |
| A1 | established +1 | established -1 | established 0 |
| A2 | established -1 | established +1 | established 0 |
| B1 | established -1 | established 0 | unseen |
| B2 | established 0 | established -1 | unseen |
| C1 | unresolved +1→-1 | established 0 | established -1 |
| C2 | established 0 | unresolved +1→-1 | established -1 |

The expected grounded-value-following choices are A1 `ADVANCE`, A2 `HOLD`, B1 `HOLD`, B2 `ADVANCE`, C1 `HOLD`, and C2 `ADVANCE`. C is descriptive uncertainty handling: selecting the unresolved relation may represent exploration, so C does not determine the primary sensitivity threshold. A and B form the six core matched comparisons per prompt condition (two pairs × three orders).

## Frozen measurements and classification

For N and G separately, count: preferred grounded choices out of 18, nonpreferred choices, choice changes under the nine value/status swaps, core A/B pairs choosing the grounded-preferred action in both variants, established negative/positive choices, unresolved/unseen choices, same action name under swap, same display position under swap, and action-name/position persistence across the three orders. The paired result uses the same action order and seed in both variants. A core pair follows grounded value only when **both** variant choices select their preregistered established preference and therefore change action accordingly.

Classify `GROUNDING_SENSITIVE_WITHOUT_DIRECTIVE` if N follows grounded value in at least five of six A/B matched comparisons, with at least two of three in each of A and B. If N misses that threshold but G meets it, classify `GROUNDING_SENSITIVE_WITH_DIRECTIVE`. If both N and G follow at most one of six and retain the same action name in at least four of nine swaps each, classify `GROUNDING_INSENSITIVE`. Other complete patterns are `MIXED`. Any invalid authoritative output, missing call, failed fixture replay, mismatched prompt, or diagnostic world execution is `INVALID`. C and order controls inform interpretation but do not alter these thresholds after inference.

If N is sensitive, the autonomous v0.2 weakness may involve sequential context or trajectory effects rather than inability to use a grounded value in isolation. If only G is sensitive, explicit authority semantics helped under matched conditions. If neither is sensitive, this study does not choose a new model, training method, or mechanical policy. No future autonomous campaign is launched automatically. These are causal claims only about changing the presented grounded assessments in the frozen matched prompts, not about long-run agent behavior.

Commit this preregistration and source hashes before building official fixtures. Then commit the authenticated derived context export and its SHA-256 manifest **before any diagnostic model inference**. Preserve complete private fixtures and calls locally. Publish only sanitized contexts, actions, hashes, metrics, and replay verdicts after a full secret-free reachable-history audit, then stop.
