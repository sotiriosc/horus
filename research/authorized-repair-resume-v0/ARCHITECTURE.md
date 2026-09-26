# Horus v0.10 authorized repair and resume

V0.10 adds a trusted operational route beside the existing behavioral and
capability-request routes. Its only capabilities are restarting the model
service, verifying the frozen model artifact, and reissuing one prediction
request for which no world action or evidence publication occurred.

The route does not grant authority to the failed request. An external grant is
authenticated first. The repair journal is HMAC chained and separate from
Memory, training records, routing evidence, and realized events. It retains
attempt 1 as `MODEL_SERVICE_FAILURE`, then binds transport attempt 2 to the
same logical prediction and exact retained request bytes.

The v0.9 `ROUTE_FAILED` record remains in the capability journal. A later
append-only resume record changes the current projection only after service
health, model-manifest, parser, and causal-eligibility checks pass. The
existing `PR-0002` probe count and ADVANCE receipt survive unchanged.

The repaired decision combines eight already durable successful decision-57
components with the one reissued HOLD joint component. It creates no new
behavioral call records. A fresh runtime/source/epoch then executes the still
missing RETREAT problem probe under the ordinary authorization and receipt
path. Subsequent assessments use fresh ordinary prediction batches.

The three authority classes remain distinct:

- behavioral: `MORE_RELATION_EVIDENCE`, which may lead to an external action;
- operational: `EXTERNAL_SERVICE_REPAIR`, which may restore infrastructure;
- capability/design: `LONGER_HORIZON_VALUE`, which remains an external-only
  request with no implementation or execution authority.

If the repaired transport fails, or if any causal precondition differs, the
route emits `REPAIR_FAILED` and stops. There is no recursive repair.
