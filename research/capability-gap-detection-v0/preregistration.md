# Horus v0.9 capability-gap detection preregistration

## Identity and frozen lineage

- Campaign: `HORUS_CAPABILITY_GAP_DETECTION_V0`
- Parent v0.8 evidence: `bc40e844fc021ca746b79551cc469c10b81c0e1d`
- Frozen implementation: `63b86b7e587c3aa00e4f62ed75636f3e7fa0cf72`
- Implementation tree: `230af6a333398fc93deda6c6a0be42b552cc206b`
- Source report SHA-256:
  `4e73a7383c7557253602cbee690c5d0b7cdf9e126d8c97217a266b60249fb11e`

V0.8 `PR-0001` remains unchanged and `UNRESOLVED`. V0.9 creates a new
successor `PR-0002`; it does not reopen, extend, or rewrite the earlier
problem's two-probe budget.

## Why live evidence is required

Deterministic retrospective analysis establishes that v0.8 had two
problem-specific RETREAT receipts and zero ADVANCE receipts. It can therefore
establish only `MORE_EVIDENCE_REQUIRED`. It cannot establish whether equal
authenticated immediate outcomes cover both tied actions. One prospective
campaign is required to acquire an ordinary authenticated ADVANCE receipt and
an ordinary authenticated RETREAT receipt under the new coverage rule, then
reassess the ordinary ranking.

## Frozen probe and assessment rules

At the first prospective observation matching the authenticated unresolved
v0.8 state-2 `[ADVANCE, RETREAT]` tie, `PR-0002` opens. The inherited persistent
failure is sufficient; two additional pre-probe abstentions are not required.

An unprobed tied action ranks ahead of every already-probed tied action.
Remaining priority is specialist disagreement, unresolved contradiction,
fewer authenticated local observations, greater staleness, then canonical
action order. Maximum problem-specific probes remain two.

The classifications are exactly `MORE_EVIDENCE_REQUIRED`,
`VALUE_TIE_RESOLVED`, `CURRENT_OBJECTIVE_CANNOT_DISTINGUISH`, and
`ROUTE_FAILED`.

`CURRENT_OBJECTIVE_CANNOT_DISTINGUISH` requires all of the following:

- both tied actions have problem-specific authenticated receipts;
- their relevant realized immediate consequences are equal;
- a later valid ordinary assessment at state 2 remains tied;
- both allowed problem evidence routes are consumed;
- no service, parse, authorization, or protected-runtime failure prevents the
  comparison.

That result requests `LONGER_HORIZON_VALUE` with
`REQUEST_REQUIRES_EXTERNAL_APPROVAL`. It does not grant calls, actions,
objective changes, model creation, training, planning, or simulator access.
If the ordinary ranking becomes unique, the result is `VALUE_TIE_RESOLVED`.
Either outcome is valid.

## Minimal prospective campaign

- Start from a byte-for-byte private clone of the completed v0.8 session and
  registry. Verify the source before and after; mutate only the clone.
- External regime remains A and is never model-visible.
- Begin one fresh runtime/source/epoch using the existing restart path.
- Maximum 12 new autonomous decisions.
- Nine unchanged model calls per decision: three joint next-state, three G2
  consequence, and three G3 consequence calls.
- Maximum 108 real calls, substantially below 486.
- Stop immediately after a terminal classification is durably completed.
- No retry, replacement call, calibration, forced receipt, hidden lookup, or
  additional runtime.
- `EPISODE_LIMIT=12` remains unchanged.

The 12-decision maximum allows the two probe executions plus ordinary actions
needed to return to state 2 for reassessment. Deterministic replay reached the
terminal question in seven decisions and 63 calls. If live behavior does not
produce and reassess the required tie within 12 decisions, classify the live
milestone as not established and stop.

Based on v0.8's measured 486-call duration of about 80 minutes 39 seconds, 108
calls are expected to take about 18 minutes, plus possible model cold-start
time. Completion is detected through a durable sentinel; intermediate model
outputs do not alter the schedule or rule.

## Failure localization and capability vocabulary

Finite localizations are `MAP_NEXT_STATE`, `MAP_CONSEQUENCE`,
`RELATION_ROUTER`, `EXPLORER_VALUE_COMPARISON`, `EVIDENCE_COVERAGE`,
`RUNTIME_CAPACITY`, `MODEL_SERVICE`, and `REPRESENTATION`.

Finite capabilities are `MORE_RELATION_EVIDENCE`, `LONGER_HORIZON_VALUE`,
`ALTERNATIVE_REPRESENTATION`, `NEW_SPECIALIST`, `NEW_RUNTIME`, and
`EXTERNAL_SERVICE_REPAIR`. Only the already-implemented relation evidence path
is automatically grantable here. Every new capability is external-approval
only.

## Frozen hashes

- `capability_gap.py`: `70ef2a28b0867618deaa4b3bdc03a42c280e79faaeb8807620f9d576635732a4`
- Capability policy: `058e64375b7a8391952437a8660b8776e4f6e00611f1285cc926f77c184133a3`
- Relation forecast integration: `4845d0fdeb34ac3101fca915f1cd5979048b4b1d80c89a91c913e8fc3962d396`
- One-shot runner: `40176e50d0b306f8df6480af00b704631a79078606833320d41f415ee450a7dc`
- Source evidence manifest: `9ea28ad1373842483aedc0a77e6707209fd877e89d35397cc4d95b9c955ed41f`

## Stop rule

Run once. Preserve any negative result or external failure. Do not tune,
resume after a campaign failure, extend past 12 decisions, start another
runtime, train, add a specialist, implement `LONGER_HORIZON_VALUE`, or begin a
follow-up experiment without new explicit authorization.
