# Horus v0.21 grounded relation reacquisition result

V0.20 was preserved unchanged at `bec668b391fb90205923fe4b6202bf25465e5696` and pushed to `build/horus-v0.20-scoped-evidence-authorization` before this milestone.

## Grounded route

The zero-inference Memory graph contained five authenticated exact transitions from state 2 to state 1. All used `RETREAT`. In chronological event order their receipt events were 22, 29, 35, 53, and 55. The frozen selector therefore chose `RETREAT` using the most recent supporting receipt, event 55 from epoch 2012. Consequence values and predicted next states did not participate in selection.

The one-use `GROUNDED_RELATION_REACQUISITION` route was authorized only for PR-0003 and target state 1, with reason `REACQUIRE_TARGET_RELATION_STATE`.

## Live result

The frozen navigation executed normally through the protected path. Its new authenticated receipt was:

| Field | Value |
|---|---|
| pre-state | 2 |
| action | `RETREAT` |
| realized consequence | 1 |
| realized next state | 1 |
| epoch | 2015 |
| event / transaction | 1 / 1 |
| source | `HORUS:a67e675004193a13c31485bad53fbb86:runtime:15:ab424125f4912c25` |

Reality confirmed the remembered transition and Horus recorded `TARGET_RELATION_REACQUIRED`. The old event-55 receipt and the new event-57 receipt are both preserved.

The process then generated and durably authenticated all nine prediction calls for decision 91, which would have been the remaining `(1, ADVANCE)` probe. Before a decision could be frozen or executed, the v0.21 integration raised `remaining scoped relation probe eligibility changed`.

The defect was in the new integration predicate. After navigation, ordinary probe cadence was legitimately available at distance 4 and the unchanged Explorer derived an ordinary `PROBE_DISAGREEMENT` decision. The v0.21 remaining-probe wrapper incorrectly reused a check requiring an abstaining `EXPLOIT_TIED_MAXIMUM` decision. The 15-property preflight test used an abstaining fixture and did not cover this ordinary-probe mode.

No patch or rerun was performed. PR-0005 records the linked `INTERNAL_ROUTE_PROBLEM`. The milestone outcome is `OPERATIONAL_FAILURE` at `REMAINING_SCOPED_PROBE_PREPARATION`.

## Preserved state

The remaining v0.20 scoped budget is unchanged at limit 2, granted 1, executed 1. No second ADVANCE receipt exists, so no six-row eviction, added row, new score, router switch, or ordinary follow-up is reported. The last completed `(1, ADVANCE)` score remains G2 3/6 and G3 4/6, with G2 selected. The established state-1 routed values remain `ADVANCE=1`, `HOLD=1`, `RETREAT=0`.

The ordinary probe marker remained at authorized decision 54. No probe budget was replenished or reset. PR-0002 is unchanged. No training ran, model weights did not change, and no global or multi-step navigation was introduced.

## Integrity and verification

The event, training, relation-routing, Explorer-confidence, and Problem-Manager chains replay or authenticate exactly. The model-call chain also authenticates through all 2,529 physical records. Because the exception occurred after the nine decision-91 calls were appended but before the session checkpoint was saved, the checkpoint registers 2,502 call records. Full `SessionStore` restart therefore fails closed on the call-head mismatch. This mismatch is preserved rather than repaired.

Post-result source tests and core regressions are reported separately in `replay-verification.json`. Their pass status does not override the live operational failure or the missing coverage revealed by it.

The narrow result is that authenticated Memory successfully reacquired the required state in one bounded execution. V0.21 did not execute the remaining relation probe or reassess specialist routing because its new handoff predicate rejected the ordinary post-reacquisition probe mode.
