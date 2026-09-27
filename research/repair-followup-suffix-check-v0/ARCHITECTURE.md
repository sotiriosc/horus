# Horus v0.18 repair and exact follow-up resume

V0.18 reuses the bounded operational-repair architecture established in v0.10. A separate authenticated repair store preserves transport attempt 1, records one service restart and health proof, then binds transport attempt 2 to the same logical prediction identity and byte-identical request.

The repair is eligible only because authenticated replay proves that decision 87 produced no external action, receipt, Memory publication, training target, or routing evidence. Eight valid sibling predictions remain durable. Only the failed `RETREAT:J` request is reissued.

After the repaired response is valid, a fresh protected runtime reconstructs the original prediction batch from those nine components. It invokes the ordinary `GroundedExplorer` without an option-profile override. The reconstruction makes no new behavioral model calls.

PR-0004 owns the operational lifecycle:

```text
REPAIR_REQUESTED
  -> REPAIR_AUTHORIZED
  -> REPAIR_ATTEMPTED
  -> REPAIR_SUCCEEDED
  -> REISSUE_ATTEMPTED
  -> RESUMED
```

Each repair event is explicitly non-behavioral and cannot enter Memory or become a training target. PR-0002 and PR-0003 remain unchanged.

If ordinary execution creates a new authenticated receipt, the retained RETREAT-profile `c1` and predicted second next state can be compared separately with reality. An abstention produces `NOT_APPLICABLE`; it does not validate a trajectory.
