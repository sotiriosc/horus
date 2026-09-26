# Horus v0.17 option-profile behavioral integration preregistration

## Frozen question

When PR-0002 is applicable at state 2 and the ordinary immediate-value maximum is exactly tied between `ADVANCE` and `RETREAT`, can the already evaluated `OPTION_PROFILE_DOMINANCE` representation select its unique dominating action before reality and return Horus to ordinary grounded operation?

## Frozen source and scope

- Parent result: Horus v0.16 commit `0c05622d7d23731a5aaec8ff185cb33f7e539044`.
- Applicable problem: exactly `PR-0002`, state 2, tied set `[ADVANCE, RETREAT]`.
- Retained result: exactly `RETREAT_PROFILE_DOMINATES`; selected action `RETREAT`.
- The v0.16 profiles, comparison rule, source evidence, and hashes must verify and reconstruct byte-for-byte before live inference.
- The behavioral allowance is one use. It does not apply to any other problem, state, tie, unique maximum, training process, or specialist route.

## Frozen intervention

For the first and only integration decision, ordinary Horus must produce valid forecasts and abstain on the exact tied maximum `[ADVANCE, RETREAT]`. The problem manager then durably records `OPTION_PROFILE_DECISION_FROZEN`, bound to the ordinary decision and forecasts, PR-0002, the exact profiles, evidence hashes, and explicit authorization. The frozen selected action is `RETREAT`.

Only that action may pass through the ordinary protected boundary. `ADVANCE` is not executed as a counterfactual. The resulting original receipt passes through Measure, authorization, Memory, routing, confidence, and problem-manager completion without substitution.

The new `RETREAT` receipt is compared with the retained grounded immediate relation: consequence `+1`, next state `1`. A difference is preserved as new contradictory evidence; it is not rewritten or retried.

After the integration decision, run at most one additional decision using the ordinary grounded Explorer. The option-profile representation does not control it. Record authorization or abstention. If it executes an action represented in the retained `RETREAT` suffix branches, compare only that branch's retained `c1` with the new realized consequence as `OBSERVED_SUFFIX_PREFIX_CHECK`. This is observational and is not complete trajectory validation.

## Frozen bounds

- Maximum fresh decisions: 2.
- Maximum local model calls: 18 (9 per ordinary prediction batch).
- Maximum option-profile executions: 1.
- Maximum ordinary follow-up decisions: 1.
- Training runs: 0.
- Retries: 0.
- New horizons, representations, objectives, simulator routes, synthetic receipts, and direct state changes: 0.

## Frozen classifications

- `INTEGRATION_EXECUTED_CONSISTENT`: a normally authorized `RETREAT` receipt reports consequence `+1` and next state `1`.
- `INTEGRATION_EXECUTED_CONTRADICTED`: a normally authorized `RETREAT` receipt differs on either field.
- `INTEGRATION_FAILED_OPERATIONALLY`: the scoped decision or protected execution cannot complete for an operational reason.

No classification globally resolves PR-0002 or claims that unexecuted `ADVANCE` would have been worse. PR-0003 must remain byte-identical in the problem-manager state.

## Stop rule

Stop after the integration decision and at most one ordinary follow-up, or immediately on a new operational/runtime defect. Do not patch and rerun. Do not train or begin another experiment.
