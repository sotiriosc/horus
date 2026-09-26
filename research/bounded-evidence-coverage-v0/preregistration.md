# Horus v0.11 bounded evidence-coverage preregistration

## Frozen lineage and question

- Parent/frozen source: `a935a4d99445eeb3f8d655deaccaf7878fed7fcd`
- Frozen implementation: `64b7cf5`
- V0.10 result: `INCONCLUSIVE_AT_BOUND`
- V0.10 public report SHA-256:
  `4c9e19a7f9fdb9f7b2402d6c6279770243224972b28226169c091f6fa51591d0`
- Source checkpoint: decision 63, 53 authorized executions, state 1
- Source problem: `PR-0002`, two problem-specific receipts, no terminal
  capability classification

The sole question is whether unchanged ordinary behavior naturally produces a
later valid state-2 tied reassessment when given twenty additional finite
decision opportunities. No result is guaranteed.

## Sole intervention and runtime segmentation

The only experimental authority is twenty fresh ordinary behavioral decisions,
in place of v0.10's five-decision continuation allowance. Each decision keeps
the existing nine-call structure, for at most 180 ordinary model calls.

The prospective protected-runtime schedule is exactly 10 + 10. Runtime segment
1 contains fresh decisions 1–10. If the campaign has not already reached a
frozen stop condition, runtime segment 2 is created immediately before fresh
decision 11 and contains decisions 11–20. This schedule is based only on the
fresh-decision index. It is not changed by state, action, outcome, accuracy,
abstention, failure, or evidence acquisition.

Both segment bounds are below `EPISODE_LIMIT=12`; that limit is unchanged. The
existing authenticated rollover path creates a fresh source identity and epoch,
projects durable prior history without reconstructing receipt capabilities, and
preserves problem, routing, exploration, and consumed repair state.

V0.10's zero-call reconstructed batch permanently offsets the ordinary request
batch count by one. V0.11 derives new decision identity from the authenticated
attempted-decision counter. It otherwise invokes the byte-identical Map,
Explorer, classifier, and execution path.

## Frozen mechanisms

There is no change to the Explorer, state-1 behavior, tie handling, probe
budget, action order, objective, model, model artifacts, prompts, sampler,
routing, receipts, Memory, state transitions, capability classifier, evidence
requirements, training, or repair policy. No action, transition, state visit,
probe, prediction, receipt, or reassessment may be forced or synthesized.

The retained repair lifecycle is `RESUMED`, with one restart and one reissue
already consumed. V0.11 authorizes zero restarts, zero reissues, and zero
infrastructure-only model health calls. It will not restore a missing service.

## Eligible reassessment

The required event must be a newly appended, authenticated
`CAPABILITY_GAP_DECISION_FROZEN` record with all of these properties:

- decision sequence greater than 63;
- ordinary pre-state exactly 2;
- ordinary decision reason `EXPLOIT_TIED_MAXIMUM`;
- all frozen forecasts valid;
- generated through the unchanged ordinary Explorer path.

Historical/replayed predictions, receipts alone, repair or health output,
fixtures, simulations, manual state injection, and externally supplied claims
are ineligible.

## Frozen stop and interpretation rules

Stop at the first of:

1. the unchanged classifier emits a terminal result;
2. ordinary execution encounters an operational/model-service failure that
   prevents continuation;
3. the unchanged protected framework rejects continuation;
4. all twenty fresh behavioral decisions are completed.

If an eligible reassessment occurs, accept only the existing classifier's
result. If it emits `CURRENT_OBJECTIVE_CANNOT_DISTINGUISH`, retain its exact
evidence chain and external-only `LONGER_HORIZON_VALUE` request without
implementing it. If it emits `VALUE_TIE_RESOLVED`, preserve that result.

If twenty decisions expire first, report `INCONCLUSIVE_AT_BOUND`. This is lack
of the required evidence, not a new capability gap. If a service failure stops
execution, report `OPERATIONAL_FAILURE`, localized to `MODEL_SERVICE`, and do
not reinterpret it as evidence about cognition, representation, or objectives.
The consumed repair authority remains consumed.

Only a mechanical proof from the frozen implementation could support
structural impossibility. Failure to revisit state 2 within this run does not.

## Frozen accounting

- Fresh behavioral decisions: maximum 20
- Runtime schedule: `[10, 10]`
- Maximum decisions in one protected runtime: 10
- Protected episode limit: 12, unchanged
- Ordinary prediction calls: 9 per decision, maximum 180
- Operational health calls: 0
- Repair calls: 0
- Training runs: 0
- Calibration, forced actions, retries, and replacement calls: 0

## Frozen hashes

- `coverage_extension.py`:
  `f8034eaa3294b611c583089ff986eb3b21426d2f3677cc3ddac71c483fc0d676`
- `coverage_extension_policy.json`:
  `b69518eb46f6a45c5f04b22b92c48b59a16c64f2500d6e418a8a40952f276a47`
- `test_coverage_extension.py`:
  `f3c019d39d4ef4858218b8219daf0a9c1cfc5a0fb02301aad45bc5e671c99f83`
- `coverage_cli.py`:
  `bda0643d7724bbaac8761d2165bf50f73b59d0e43f85d65d47940cd5f9fc5034`

## Final stop

Run once and preserve the actual outcome. Do not tune, repair, retry, extend,
change state-1 policy, implement `LONGER_HORIZON_VALUE`, train, or begin a
follow-up experiment.
