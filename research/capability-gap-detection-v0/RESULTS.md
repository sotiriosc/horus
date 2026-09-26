# Horus v0.9 capability-gap detection results

## Result

The finite capability-gap mechanism and improved tie-probe coverage passed all
zero-inference validation. The one prospective live campaign then terminated
honestly as `ROUTE_FAILED` because a joint next-state call timed out before the
second tied action could receive a receipt.

The live campaign therefore does **not** establish
`CURRENT_OBJECTIVE_CANNOT_DISTINGUISH` and did not emit
`LONGER_HORIZON_VALUE`. It correctly distinguished “cannot proceed” from
“cannot distinguish,” localized the failure to `MODEL_SERVICE`, requested
`EXTERNAL_SERVICE_REPAIR`, and stopped with no retry.

## Identity and taxonomy

- Branch: `build/horus-v0.9-capability-gap-detection`
- Parent v0.8: `bc40e844fc021ca746b79551cc469c10b81c0e1d`
- Implementation: `63b86b7e587c3aa00e4f62ed75636f3e7fa0cf72`
- Preregistration: `4c87c5f`
- Preflight: `245fc37`

Assessments are `MORE_EVIDENCE_REQUIRED`, `VALUE_TIE_RESOLVED`,
`CURRENT_OBJECTIVE_CANNOT_DISTINGUISH`, and `ROUTE_FAILED`. Capability requests
are `MORE_RELATION_EVIDENCE`, `LONGER_HORIZON_VALUE`,
`ALTERNATIVE_REPRESENTATION`, `NEW_SPECIALIST`, `NEW_RUNTIME`, and
`EXTERNAL_SERVICE_REPAIR`.

Localizations are `MAP_NEXT_STATE`, `MAP_CONSEQUENCE`, `RELATION_ROUTER`,
`EXPLORER_VALUE_COMPARISON`, `EVIDENCE_COVERAGE`, `RUNTIME_CAPACITY`,
`MODEL_SERVICE`, and `REPRESENTATION`.

## Retrospective v0.8 analysis

`PR-0001` remains unchanged and `UNRESOLVED`. It contained two authenticated
problem-specific RETREAT receipts, both consequence +1 and next state 1, but no
problem-specific ADVANCE receipt. V0.9 therefore retrospectively classifies
the available evidence as `MORE_EVIDENCE_REQUIRED`, localized to
`EVIDENCE_COVERAGE`. A representation gap cannot be inferred from that
one-action coverage.

## Minimal prospective design and execution

The campaign cloned the completed private v0.8 state without modifying its
source, began one fresh runtime in regime A, allowed at most 12 decisions and
108 calls, and stopped at the first terminal classification. Deterministic
replay reached the intended assessment in seven decisions and 63 calls. The
live run stopped after three decisions and 27 calls.

| Measure | Result |
|---|---:|
| New decisions | 3 / 12 maximum |
| New model calls | 27 / 108 maximum |
| New authorized executions | 2 |
| New abstentions | 1 |
| Calibration executions | 0 |
| Retries or replacement calls | 0 |

## Complete problem evolution

1. The unchanged `PR-0001` history was imported by hash with status
   `UNRESOLVED`; it was not rewritten.
2. Decision 55 observed the same authentic state-2 ADVANCE/RETREAT tied maximum
   and opened successor `PR-0002`.
3. The coverage-first rule selected previously unprobed `ADVANCE`, rather than
   repeating RETREAT. The broker requested and used the existing
   `TIE_INFORMATION_PROBE` route.
4. The decision-55 receipt authenticated `ADVANCE`: predicted next state 3,
   realized immediate consequence +1, realized next state 3.
5. Decision 56 used the ordinary unique maximum at state 3, selected RETREAT,
   and received consequence +1 / next state 2. This returned naturally to the
   problem state.
6. Decision 57 attempted the reassessment needed to select the still-unprobed
   RETREAT action. One joint next-state request ended in `TimeoutError`, making
   the Map component invalid.
7. The problem appended `ROUTE_FAILED`, localized resolution stop to
   `MODEL_SERVICE`, requested `EXTERNAL_SERVICE_REPAIR`, and ended
   `UNRESOLVED`. No replacement call was made.

## Tied-action evidence and capability request

| Tied action | Problem-specific receipt | Predicted next state | Realized consequence | Realized next state |
|---|---|---:|---:|---:|
| ADVANCE | decision 55 | 3 | +1 | 3 |
| RETREAT | none | — | — | — |

Immediate evidence did not resolve the tie, but coverage was incomplete, so it
also could not establish that immediate-consequence representation was
insufficient. The emitted capability was `EXTERNAL_SERVICE_REPAIR`, supported
by the recorded joint-call `TimeoutError`. Its authority status was
`REQUEST_REQUIRES_EXTERNAL_APPROVAL`; it could not call a model, retry,
execute, train, change the objective, or create an architecture.

`LONGER_HORIZON_VALUE` remains defined only as a typed future interface and was
not implemented, granted, or live-requested.

## Replay, verification, and limitations

The original v0.8 session and registry commitments were identical before and
after the run. Capability history, the successor problem, its consumed probe
budget, and the terminal escalation survived authenticated restart replay.
Two independent reports were byte-identical with SHA-256
`70e1b60a80bfd1e819de5e4433c912500b02f3ded4176c8ee6855a2a7c556592`.

- 15/15 focused capability-gap tests passed.
- 114/114 full Horus Python tests passed.
- 53/53 core regression steps passed.
- Hidden regime/law checks passed for all 27 new requests.

The key live milestone remains unestablished because RETREAT did not receive a
problem-specific receipt. The deterministic logic demonstrates the intended
classification under controlled evidence, but that is not a substitute for
the missing live authenticated comparison. The frozen stop rule forbids a
retry or replacement campaign without new authorization.
