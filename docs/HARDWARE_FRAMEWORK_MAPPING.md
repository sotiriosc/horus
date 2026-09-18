# Hardware-to-framework mapping after base framework v0

**Status:** the complete five-component loop is IMPLEMENTED in bounded software.
The independent-authorization primitive is separately IMPLEMENTED in RTL. The
new hardware primitives below are PROPOSED; they have not been synthesized or
timed.

| Framework component | Current software implementation | Existing Horus primitive | Required new hardware primitive | Bounded state cost in v0 | Authority boundary | Evidence boundary |
|---|---|---|---|---|---|---|
| Explorer | `Explorer` scores three actions from up to eight audited records | `horus_controller` sequencing and router transport | Three-way policy selector carrying epoch, transaction, state, and Map version | Three scores plus one proposal; no persistent private state | `ActionAuthority` alone permits environment execution | Current protected state snapshot; Explorer output is never evidence of correctness |
| Map | `MapModel` holds one versioned incumbent and computes one prediction | `skpr` local state/tags; block registers | Versioned state register, prediction interface, one-entry quarantine, two candidate slots | One incumbent, at most two candidates, one quarantined incumbent | `StateAuthorizer` controls Map commit | Provenance-matched external state/consequence receipt |
| Measure | `Measure` proposes a verdict; `EvidenceAuditor` recomputes it | Gap detector/comparators; bounded commit numerical checker | Receipt/prediction comparison adapter with separate verdict output | One prediction, receipt, and verdict per transaction | Auditor verdict contributes to composite commit; Measure cannot authorize | Immutable environment consequence receipt and independent recomputation |
| Memory | `OutcomeMemory` plus paired `ProtectedEvidenceStore` rings | Input/router buffers, keeper state, protected-record storage | Eight-entry audited outcome ring paired with eight-entry protected receipt ring | 8 outcome records + 8 protected receipts + 1 quarantine | `RecordAuthorizer` controls insert/rebuild; paired rotation is atomic | Exact epoch, transaction, observation, source, transition, consequence, and prior authorization |
| Recovery | `Recovery` proposes one state, measurement, or record correction | Repair/replay wrapper plus bounded independent commit gate | Failure-class adapter and one-candidate recovery mux feeding existing authorization gate | 1 attempt, 1 candidate, 1 quarantine per affected subsystem | Existing-style separate authorizer accepts/rejects; Recovery has no commit output | Protected receipt; no repaired-output-derived reference |
| Coordinator / continuation | `BaseFramework` stages Map and Memory updates and stops on rejection | Valid/ready backpressure and `commit_valid` boundary | Small transaction FSM joining action, state, record, and continuation grants | 12 steps, 16 trace records, one active transaction | Continuation only after every mandatory grant | Transaction-wide identity must remain consistent across all gates |

## Reuse boundary

The prior bounded commit gate supplies the tested policy pattern for Recovery:
protected source record, quarantine, identity/content check, then downstream
authorization. Base framework v0 reuses that authority separation in software;
it does not replace the protected checker with the older SKPR detector or the
repair producer. SKPR detection and replay can propose a candidate, but neither
is causally independent of that candidate.

The software StateAuthorizer and RecordAuthorizer are architectural models, not
claims of new RTL. Hardware integration would adapt the existing bounded gate
to the framework's observation/source fields and would need to preserve the
same non-descendant evidence path.

## State and cost implications

The earlier no-trace authorization gate measured about 29,929 µm² in its
standalone Sky130 probe. Separate component probes attributed most observed
cost to protected-record and quarantine storage/access, with smaller numerical
checker and identity comparison probes. Those probes are not an additive area
decomposition because synthesis shares and restructures logic.

No area number is assigned to base framework v0. Its Python objects do not
define register widths, ports, timing, arbitration, reset behavior, or physical
protection. The first RTL mapping should preserve the frozen functional limits
before testing compression, sampling, or moving observational trace off the
critical path. The authorization decision itself must retain enough protected
state to recompute the declared predicate.

For this software experiment the minimum accepted identity is `(epoch,
transaction_id, observation_id, source_identity)`. The older hardware tuple
`(epoch, transaction_id, source_record_id)` remains sufficient only under its
single-source immutable-record assumptions. Dropping `source_identity` in a
future multi-source design would weaken binding; dropping `observation_id`
would merge pre-state and post-action receipts for the same transaction.

## Authority path proposed for hardware

```text
Explorer proposal
  → action/provenance gate
  → environment or accelerator execution
  → protected consequence receipt
  → Measure proposal + independent comparison
  → incumbent/candidate quarantine and selection
  → protected-source state authorization
  → protected-source Memory authorization
  → atomic Map/Memory commit
  → continuation grant
```

The trace is observational in both the existing gate and the proposed mapping.
It may be packed or exported if decisions and required forensic records remain
identical. Protected receipts are decision inputs and cannot be sampled away or
replaced by candidate-derived summaries merely to reduce cost.

## Evidence for the mapping

- The complete software loop and all authority boundaries passed the
  [predeclared campaign](../research/base-framework-v0-results.md).
- The prior RTL gate passed 4,200 protected-path transactions, and its broader
  campaign passed 2,700 transactions under the documented trust boundary.
- The full finite Map/environment state space was cross-checked in 12 cases.
- No complete-loop RTL, timing, power, placement, multi-clock behavior, or
  common-mode protected-source fault result exists yet.

## What the mapping does not establish

This table does not turn routing, arithmetic, or finite-state control into a
general Explorer or world model. It does not show semantic truth, general
causal independence, general self-correction, or hardware feasibility at a
target frequency. Each required new primitive remains PROPOSED until separately
specified, implemented, and tested.
