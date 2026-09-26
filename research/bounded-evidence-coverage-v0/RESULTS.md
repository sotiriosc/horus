# Horus v0.11 bounded evidence-coverage results

## Result

The single prospective v0.11 run completed both preregistered ten-decision
runtime segments and ended `INCONCLUSIVE_AT_BOUND` after exactly twenty fresh
ordinary behavioral decisions.

All twenty decisions began and ended in state 1. Every nine-call prediction
batch was valid. The unchanged Explorer observed a tied routed maximum on every
decision, had no ordinary probe budget available, and abstained. No world
execution occurred, state 2 was never revisited, and no eligible ordinary
state-2 tied reassessment was produced.

The existing classifier therefore emitted neither
`CURRENT_OBJECTIVE_CANNOT_DISTINGUISH` nor `VALUE_TIE_RESOLVED`.
`LONGER_HORIZON_VALUE` was not requested or implemented. The retained problem
remains `MORE_EVIDENCE_REQUIRED`, localized to `EVIDENCE_COVERAGE`.

## Lineage and intervention

- Branch: `build/horus-v0.11-bounded-evidence-coverage`
- Parent v0.10: `a935a4d99445eeb3f8d655deaccaf7878fed7fcd`
- Implementation: `64b7cf5`
- Preregistration: `3db00c5`
- Preflight: `1ec15f4`
- Sole intervention: twenty additional ordinary decision opportunities
- Runtime segmentation: ten decisions in runtime 9, then ten in runtime 10
- Protected `EPISODE_LIMIT`: 12, unchanged

The rollover before fresh decision 11 followed the preregistered index-only
schedule. Runtime 9 used epoch 2009 and a fresh source identity; runtime 10 used
epoch 2010 and another fresh source identity. Durable Memory/history, problem
state, routing, exploration, and consumed repair authority survived both
boundaries. No old receipt object was reconstructed.

## Accounting

| Measure | Result |
|---|---:|
| Fresh behavioral decisions | 20 / 20 |
| Ordinary prediction calls | 180 / 180 |
| Joint next-state calls valid | 60 / 60 |
| G2 consequence calls valid | 60 / 60 |
| G3 consequence calls valid | 60 / 60 |
| Operational health calls | 0 |
| Repair calls | 0 |
| Authorized world executions | 0 |
| Abstentions | 20 |
| State-2 visits | 0 |
| Valid state-2 tied reassessments | 0 |
| Training runs | 0 |

The exact trajectory is decisions 64–83, each with pre-state 1, valid
predictions, `EXPLOIT_TIED_MAXIMUM`, no selected action, `ABSTAINED`, and
post-state 1. The machine-readable report retains every decision sequence and
both runtime boundaries without publishing prompts or raw responses.

## Classification and retained request

The finite bound expired before the required observation. This is lack of the
required evidence. It is not evidence that the condition is structurally
unreachable, not evidence that Horus lacks a representational capability, and
not evidence that equal immediate outcomes require longer-horizon value.

The classifier remains nonterminal. The retained request is
`MORE_RELATION_EVIDENCE` through the existing behavioral route, with
localization `EVIDENCE_COVERAGE`. V0.11 grants no further decisions or policy
change.

There was no operational failure. The inherited repair journal remained
`RESUMED` with one consumed restart and one consumed reissue; v0.11 neither
replenished nor used repair authority.

## Verification and interpretation

The completed v0.10 private source commitments are unchanged. All private
session, capability-gap, exploration, routing, and repair stores reopened and
replayed. Two independently generated reports were byte-identical with SHA-256
`1a942e2bca630c7a9a453a8140fcd6c4d3f1c59c2bdd02adb3851370813cabcc`.

- 12/12 focused v0.11 tests passed before and after live execution.
- 142/142 full Horus Python tests passed before and after live execution; the
  final run took 26.504 seconds.
- 53/53 core regression steps passed before and after live execution.

V0.11 establishes that increasing the window from five to twenty unchanged
ordinary decisions did not yield a state-2 revisit in this run. It does not
establish that no legal route to state 2 exists. The repeated valid state-1
tied abstentions suggest that a future isolated study could examine the
state-1 exploration policy, but this milestone does not modify that policy or
authorize such a study.
