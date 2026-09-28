# Frozen comparison: `I` versus `S`

| Boundary | `I = INCUMBENT` | `S = STAGNATION_ESCAPE` |
| --- | --- | --- |
| Base source | Completed grounded-authority [protocol](../../experiments/grounded_authority_autonomous_agent_v0/protocol.py) and [worker](../../experiments/grounded_authority_autonomous_agent_v0/worker.py), preserved at `0d3efe0` | Same source and behavior except the single proposed pre-selection override in [candidate-rule](candidate-rule.md) |
| Established `+1` exact deterministic relation | Mechanical global-ceiling choice | Identical; escape never eligible |
| All exact deterministic actions established | Mechanical maximum choice | Identical; no unseen alternative |
| Mixed route without qualifying streak | Model chooses among incumbent candidates; strict one-field parse | Identical model authority, candidates, prompt, parse, and parameters |
| Mixed route after three qualifying same-state zero fallbacks, with unseen alternative still present | Model remains free to choose the known zero or an uncertain candidate | One mechanical action selects first still-unseen action in `ADVANCE`, `HOLD`, `RETREAT` order; no action-model call for that selection |
| After escape receipt | Not applicable | Original protected receipt admitted normally; ordinary incumbent route resumes; new streak starts at zero |
| Self-review | Separate, non-authoritative; no proposal feedback into decisions | Identical; no self-modification or new review authority |
| Recovery | Existing signed SessionStore and ModernMemory reconciliation | Identical, plus read-only reconstruction of qualifying suffix from authenticated records; no new mutable grounded counter |

The sole candidate distinction is an action-selection boundary. S must not change the protected executor, original receipt trust, Measure, authorization, durable Memory, deterministic or empirical fold, `UNRESOLVED` status, action validity, world/task family, goal, model identity/parameters, run length, or restart semantics in a future comparison. A future implementation would be new candidate code, never an in-place edit of I. These invariants make an observed difference in relation sampling interpretable as the proposed rule's effect rather than a changed evidence path.

The rule's mechanical action is an information-acquisition decision, not a claim that the unseen action is better. It is deliberately outside model preference only at the exact trigger; all genuinely unknown choices outside it remain under I's existing mixed-route model authority. No hidden schedule phase or unexecuted consequence may enter either arm's decision context.
