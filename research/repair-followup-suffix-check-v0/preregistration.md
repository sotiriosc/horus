# Horus v0.18 repair, follow-up resume, and suffix-prefix preregistration

## Frozen source

- Parent: Horus v0.17 commit `5efc3803ca8b7ece8a01021ba912a6292fe64448`.
- V0.17 evidence manifest SHA-256: `a1cf44f6150fa1eb315bb9dc66922e8587c526d787985e9e83f466ed64e39150`.
- PR-0002 result remains `INTEGRATION_EXECUTED_CONSISTENT`.
- Operational problem: `PR-0004`, caused by a timeout before execution during the one permitted ordinary follow-up.
- Failed logical prediction identity: `a67e675004193a13c31485bad53fbb86:e2012:option-profile-integration:d87:RETREAT:J`.
- Request SHA-256: `d2541b9cf79573ec0b33b281568ed93032d77ff346310b90b6148288f14f4e6f`.
- Exact transport-body SHA-256: `ca5407171f21954fef0ee767b329cb14e6ecb2dc6c8559bc26b4b527c793870b`.
- Failed response SHA-256: `9e177280df0d138c5d65e05b99bb075132b0ea61e91123edd18f9234f9a87a97`; error `TimeoutError`.

## Zero-call eligibility gate

Before any live call, authenticated replay must show:

1. decision 87 executed no external action;
2. it created no receipt or Memory publication;
3. it created no routing evidence;
4. its original request and exact transport bytes remain durable;
5. all eight sibling predictions have valid durable parsed responses;
6. current state and Memory are unchanged since that abstention;
7. PR-0004 remains the applicable operational problem;
8. v0.17 evidence is byte-identical.

Failure of any condition produces `REPAIR_INELIGIBLE` with zero live calls.

## Frozen repair authority and bounds

Only `RESTART_MODEL_SERVICE`, `VERIFY_MODEL_ARTIFACT`, and `REISSUE_UNEXECUTED_PREDICTION_REQUEST` are authorized.

- Maximum service repairs: 1.
- Maximum transport reissues: 1.
- Infrastructure parse-health model calls: 1.
- Exact repaired transport model calls: 1.
- Other model calls: 0.
- Total live model-call ceiling: 2.
- Resumed ordinary behavioral decisions: exactly 1 if repair succeeds.
- Training runs: 0.
- No prompt, sampling, model, representation, objective, routing, or policy changes.

Attempt 1 remains immutable. Attempt 2 uses the same logical prediction identity, a distinct transport-attempt identity, and byte-identical request content. The eight valid sibling predictions are reused and are never regenerated.

## Frozen resume

On successful repair, reconstruct the incomplete state-1 batch from the eight durable sibling results and the single repaired response. A fresh protected runtime may carry the resumed decision, but the behavioral context, authenticated Memory, routing state, Explorer policy, request bytes, and logical failed-request identity remain unchanged.

The ordinary `GroundedExplorer` alone derives the resumed action. Option-profile dominance has no follow-up authority. The result may execute through the normal protected chain or legitimately abstain.

## Frozen observations

If an ordinary action executes, compare its new authenticated consequence with the retained RETREAT-profile `c1` for that second action:

- `ADVANCE`: `+1`
- `HOLD`: `+1`
- `RETREAT`: `0`

Report `OBSERVED_SUFFIX_PREFIX_CHECK` as `MATCH`, `MISMATCH`, or `NOT_APPLICABLE`. Separately compare the retained predicted second next state (`ADVANCE`: 2, `HOLD`: 1, `RETREAT`: 0) with the realized next state. Both retained fields remain labeled predictions. Neither comparison globally validates or invalidates `OPTION_PROFILE_DOMINANCE`.

## Outcomes and stop rule

- `ORDINARY_CONTINUATION_EXECUTED`
- `ORDINARY_CONTINUATION_ABSTAINS`
- `REPAIR_FAILED`
- `REPAIR_INELIGIBLE`

Stop after one repaired transport attempt and one resumed ordinary decision, or immediately on failure. Do not patch, retry, extend, train, or begin another experiment.
