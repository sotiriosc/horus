# Constraint provenance for frozen E

| Bound | Provenance label | Meaning |
| --- | --- | --- |
| Empirical window and minimum suffix length **4** | `EMPIRICALLY_SUPPORTED_RULE / existing empirical-state parameter` | Reuses the already frozen four-observation empirical window tested in the stochastic study. It is not a runtime workaround or a newly reward-fitted exploration threshold. The original study froze it as an experiment control; support is bounded to that empirical representation. |
| Recent four-consequence sum **≤0** | `SELECTED_PHASE3_HYPOTHESIS` | Natural zero sign boundary selected in the preserved H2 diagnosis; observed outcomes only. |
| All-observation cumulative sum **≤0** | `SELECTED_PHASE3_HYPOTHESIS` | Same H2 zero boundary across the exact relation's authenticated receipts; avoids recent-only signals on the preserved stationary-future ambiguity. |
| Consecutive same `(state, action)` and self-loop receipts | `ARCHITECTURAL_SAFETY_BOUND` | Prevents treating a changed state/action or an ongoing acquisition as stagnation. Any non-authorized event breaks the suffix. |
| Canonical `ADVANCE, HOLD, RETREAT` choice order | `EXISTING_ARCHITECTURAL_DETERMINISM` | Reuses existing action order; target selection is deterministic and model-free. |
| Established deterministic **+1** exclusion | `EXISTING_GROUNDED_AUTHORITY_BOUNDARY` | Existing authoritative ceiling wins; E cannot override it. |
| Exclude `POSSIBLE_REGIME_CHANGE` | `ARCHITECTURAL_SAFETY_BOUND` | Avoids an E intervention while the empirical fold explicitly tracks a candidate change. |
| Exact `UNSEEN` with zero observations | `ARCHITECTURAL_SAFETY_BOUND` | The action must acquire missing relation evidence; unresolved or observed empirical relations are not missing. |
| S threshold **3** and deterministic established-zero eligibility | `EMPIRICALLY_SUPPORTED_RULE` | Frozen promoted S remains separate and untouched. E's four-window condition does not retune S. |

Episode length, model context size, prediction-token caps, review cadence, and restart split are **not** E eligibility parameters. The prior [diagnosis inventory](../empirical-information-stagnation-diagnosis-v0/constraint-provenance.md) classifies those campaign controls; none is relabeled an architectural invariant or changed here.
