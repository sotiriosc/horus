# Horus v0.17 scoped behavioral integration

The integration is a one-use adapter between the ordinary grounded Explorer and the existing problem manager. It is eligible only for PR-0002 at state 2 when ordinary routed consequences are valid and the maximum is exactly tied between `ADVANCE` and `RETREAT`.

The adapter first runs the ordinary Explorer. It then asks the problem manager to verify the exact v0.16 profile evidence commitment and the consumed one-use authorization. The manager appends `OPTION_PROFILE_DECISION_FROZEN` before the protected execution boundary. That record binds the ordinary decision, current forecasts, exact profiles, applicable problem, representation result, and selected `RETREAT` action.

The normal runtime then performs:

```text
frozen RETREAT
  -> protected begin_step
  -> external execution
  -> original receipt
  -> Measure / authorization / Memory
  -> routing and confidence updates
  -> problem-manager completion
```

No counterfactual action is executed. The new receipt is appended beside retained evidence. The integration classification compares only the retained grounded first-step relation with the new authenticated receipt.

Afterward, at most one decision uses the ordinary `GroundedExplorer` directly. The problem manager records its outcome as an observation of the PR-0002 integration, without applying option-profile control and without changing PR-0003. A suffix-prefix comparison is available only if this ordinary follow-up executes a retained second action.

The representation is not installed as a global objective. It has no training, specialist-routing, simulator, receipt-issuance, Memory-writing, or self-authorization authority.
