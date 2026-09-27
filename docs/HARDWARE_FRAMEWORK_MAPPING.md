# Hardware-to-framework mapping after base framework v2

## V2 evidence-package boundary

Base framework v2 is IMPLEMENTED in bounded software. Every v2 RTL item below
is PROPOSED; none was implemented, synthesized, timed, placed, or optimized.

| V2 function | Existing Horus primitive | Possible RTL primitive | New required state | Authority boundary | Evidence boundary |
|---|---|---|---|---|---|
| Process registry | Static configuration and protected-record descriptors | Nine-entry read-only dependency ROM with version | 9 fixed nodes; process, parent, domain, type, role | Supplies facts only; cannot authorize | Must be protected from candidate writes and version-bound |
| Source-pair validator | Bounded identity/numerical checker | A/B provenance and equality comparator | Two full receipts per round | Produces pair-valid input only | Registered ports, epoch, transaction, sequence, observation IDs |
| Witness generator/interface | World-side consequence/status interface | Separate four-bit transition-relation adapter | One code plus identity per round | Produces data only | Must not derive from A/B or repaired candidate |
| Witness checker | Small integer specification comparator | Encode A/B claim and compare four-bit C | One comparison result | Cannot authorize alone | Binds C to exact epoch, transaction, sequence, and process |
| Package assembler | Quarantine/association buffers | Three-slot A/B/C join keyed by transaction | 3 items; 1 active package | Withholds inherited v1 interface until complete | Retains two observation IDs, witness ID, path triple, registry version |
| Declared separation validator | Identity/fault-domain checking pattern | Small ancestor/domain walk or precomputed compatibility matrix | Fixed nine-node relation state | Supplies separation grant only | Rejects registered shared/derived paths; cannot find undeclared causes |
| Quarantine | Existing two-entry quarantine | One-package quarantine record | 1 transaction | Blocks Map/Memory/continuation | Preserves the complete disputed package identity |
| Re-observation controller | Replay FSM/backpressure | One retry-used bit and sequence increment | 1 retry; 2 rounds | Requests fresh evidence only | Same transaction/action with fresh sequence and item identities |
| Authorization gate | Protected-source commit gate | Join of package, Measure, state, Memory, and continuation grants | 8 package decisions aligned with 8 pair/Memory records | Sole complete-package admission to commit path | Atomic identity-preserving package/pair/Memory rotation |

```text
registered A ─┐
registered B ─┼→ package assembler → provenance + declared-separation gate ─┐
witness C ────┘                                                            │
registry ROM ───────────────────────────────────────────────────────────────┘
                    disagreement → quarantine → one re-observation → stop
                                               │ authorized package
                                               ▼
                              unchanged v1 Measure/state/Memory gates
                                               │
                                      atomic commit/continue
```

The four-bit witness is smaller than a full third receipt, but its independence
is architectural, not implied by width. The package trace is observational and
may later be packed or exported. The active transaction identity, registry
version, required receipts, witness relation, and decision grants cannot be
sampled away without changing the tested authorization predicate.

The two negative controls define the hardware trust boundary. Identical wrong
A+B+C relations passed in 3/3 runs, and a false registry passed derived B/C in
3/3 runs. Physical implementation would need separately tested protection for
the registry and witness path before claiming more than declared separation.

## V1 cross-source observation boundary

Base framework v1 is IMPLEMENTED in software only. The table maps its new
observation-boundary functions to existing support and possible RTL. Every new
RTL item remains PROPOSED; none was synthesized, timed, or area-optimized.

| V1 function | Existing Horus primitive | Possible RTL primitive | New bounded state | Authority boundary | Provenance boundary |
|---|---|---|---|---|---|
| Source A | External protected-record input and existing scoreboards | Table-oriented observation adapter on registered port A | One immutable receipt per round | Produces data only | Fixed A port, source ID, epoch, transaction, sequence, observation ID, domain A |
| Source B | Separately implemented checker/specification pattern | Structurally different conditional observation adapter on registered port B | One immutable receipt per round | Produces data only | Fixed B port and equivalent B-specific identity/domain fields |
| Pairing | Two-entry quarantine and protected-record association | Two-slot pair buffer keyed by epoch/transaction/sequence | Two receipts; one active transaction | Cannot authorize from one slot | Both registered ports, distinct observation IDs, equal transaction/action/pre-state |
| Disagreement detector | Comparators in bounded commit gate | Fieldwise next-state/consequence and provenance comparator | One disagreement code | Requests quarantine/re-observation; cannot select a source | Preserves both original receipt identities |
| Quarantine | Existing bounded commit quarantine storage | One-transaction dual-receipt quarantine | One transaction | Blocks Map/Memory commit and continuation | Exact disputed pair and round identity |
| Re-observation control | Replay FSM and valid/ready backpressure | One-bit retry-used flag plus sequence increment and stop state | One attempt, two rounds total | May request observations; cannot fabricate or accept them | Same epoch/transaction/action with fresh sequence/observation IDs |
| Cross-source authorizer | Independent identity/numerical checker pattern | Registered-port, lineage/domain, provenance, and agreement gate | One pair-decision identity; at most 24 authorization identities/epoch | Sole pair authorization grant | Accepts only registered A+B, declared distinct domains, external lineage, exact pair match |
| Memory commit gate | Protected-source commit gate and bounded storage | Atomic join of pair grant, Measure audit, state grant, and eight-entry paired rings | Eight Memory records + eight pair decisions | Commits only after every grant | Stores pair decision/source identities with authorized consequence |

The runtime path is:

```text
registered A receipt ─┐
                      ├→ pair/provenance/independence gate
registered B receipt ─┘             │
                           disagreement → one re-observation → stop if unresolved
                                     │ authorized pair
                                     ▼
Map prediction → Measure audit → candidate/quarantine → Recovery proposal
                                     │
                          state + Memory authorizers
                                     │
                         atomic commit and continuation
```

The common-mode control demonstrates the boundary of this mapping. Identically
wrong A and B receipts passed the structural pair gate. During recovery, the
pair outweighed the disagreeing Map prediction and caused a false commit. Port
duplication, extra comparators, or metadata alone do not establish genuine
fault-domain diversity. A hardware implementation must retain this limitation
until a separate diversity/trust experiment supplies a tested rule.

## V0 five-component mapping

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
