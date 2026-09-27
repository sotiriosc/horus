# Post-run validity audit

The single preregistered campaign and its exact replay completed. A final code
audit found one material boundary defect.

The neutral harness created receipt-shaped value records and protected its log
with a deterministic HMAC/hash chain. It did **not** execute through the current
Horus `ExternalExecutionBoundary`, protected receipt capabilities,
`StatusBoundFramework`, or its independent authorizer. The HMAC key derivation is
also present in the public harness, so the chain is replayable tamper evidence,
not an independent authorization boundary.

Consequences:

- Model requests/responses, strict parsing, component toggles, event schedule,
  actions, predictions, consequences, timing, and router/Explorer decisions are
  preserved and exactly replayable.
- The field named `authorized_executions` in frozen `results.json` counts logged
  external executions. It must not be interpreted as proof that protected Horus
  authorization accepted them.
- “Original receipt,” causal-capability identity, fail-closed authorization, and
  protected restart-integrity outcomes are **NOT ESTABLISHED** by this campaign.
- The Horus condition exercised its current pure router/history/Explorer policy
  surfaces, but not the full v0.22 durable evidence stores, problem manager, or
  route-handoff recovery.

This defect does not justify editing the completed raw evidence or silently
rerunning after observing outcomes. The results report narrows its claims. Any
replacement requiring the protected execution boundary must be separately
preregistered and authorized.

