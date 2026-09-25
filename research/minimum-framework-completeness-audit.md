# Minimum-framework completeness audit

**Recommendation B — CORE CORRECTION REQUIRED.** All five functional components
and the causal Memory loop exist. The current implementation is not yet
minimum-complete under the frozen audit criterion: three existing enforcement
relationships fail. This calls for bounded corrections to current code, not
another source, witness, checker layer, or larger world.

Baseline: public main `b8e4245ef14b11ee5d94ce851aec4d8dc059963f`.
Completion definition: `ba905e9`. Stress preregistration: `e46331b`.
Test-only harness: `4671b70`. No v0/v1/v2 runtime or historical result was changed.
The compact [audit evidence](../experiments/minimum_framework_audit/results.json)
contains case outcomes, examples, and the exact executed source hashes.

## 1. Frozen completion definition

The [completion definition](minimum-framework-completion-definition.md) was
committed before the new code audit. It requires the fourteen functions below,
working together within the declared scope. Explicit, bounded, candidate-external
roots of trust are permitted; eliminating every assumption is not required.

An essential contract failure selects B. An unestablished invariant without a
demonstrated failure selects C. A requires all essential functions and covered
criteria to pass. Previously published outcomes were known; preregistration is
chronological, not a claim of prior-result blindness.

## 2. Completeness matrix

Statuses refer to the implemented obligation, not to whether the whole campaign
passed. MISSING CORE CAPABILITY here means a missing enforcement relationship
within an existing component; it does not imply a new architectural component.

| Required function | Original intent | Current implementation | Demonstrating test | Negative control / gap | Status |
|---|---|---|---|---|---|
| Explorer | bounded proposed action | v0 `Explorer.scores/choose`; v1 `begin_step` | clean loop; invalid-action/stale-Map rejection | Memory-audit ablation changes choice | IMPLEMENTED + TESTED |
| Map | revisable prediction separate from truth | v0 `MapModel`, reused by v1/v2 | snapshot before oracle execution; state recovery | trusted driver can replace pending Prediction reference | IMPLEMENTED BUT WEAKLY TESTED |
| Measure | compare prediction with consequence | v0 Measure/auditor; v1 `MeasureAuditor` and measurement construction | wrong Measure + stale C corrected | forged late prediction can manufacture confirmation under driver replacement | IMPLEMENTED BUT WEAKLY TESTED |
| Memory | authorized history affects action | v1 `CrossMemory` plus pair store and v2 package ring | history/ablation pairs; corruption before behavior | descending epoch recovery misaligns paired rings | IMPLEMENTED BUT WEAKLY TESTED |
| Recovery | bounded proposal after failure | v1 `Recovery`, followed by state/Memory/Measure checks | stale state and combined faults | self-authorization ablation changes Map incorrectly | IMPLEMENTED + TESTED |
| External consequence | evidence not made by judged candidate | unchanged A/B implementations; C table; world-side request | correct-C source-fault tests | A+B+C and false registry controls | ASSUMED / TRUST ROOT |
| Proposal/authorization separation | no proposer can bypass mandatory grant | package authorizer and inherited gates exist | normal incomplete package stays staged | exposed v1 receipt method commits without C | MISSING CORE CAPABILITY |
| Provenance | correct transaction/state/epoch/source | receipt coordinates, decision IDs, paired stores | stale/duplicate/epoch tests | numeric epoch sorting breaks chronological association | IMPLEMENTED BUT WEAKLY TESTED |
| Failure gating | failure withdraws continuation | `_dispute`, `_reject`, pending guards | repeated rejection; final retry; full quarantine | delegated v1 ingress bypasses v2 requirement | IMPLEMENTED BUT WEAKLY TESTED |
| Independent recheck | recovery uses valid external relation | package code comparison then state check | valid recovery and invalid-recovery controls | absent numeric domain check permits correct-C alias false accepts | MISSING CORE CAPABILITY |
| Incumbent/candidate policy | retain valid incumbent; reject invalid one | `_complete_pair` compares incumbent with admitted decision | valid HOLD incumbent; invalid ADVANCE incumbent | weakened selector still stopped by state authorizer | IMPLEMENTED + TESTED |
| Bounded state | finite storage and attempts; paired rotation | fixed rings, traces, retry and quarantine checks | eight-entry eviction; two-round exhaustion | order failure despite all cardinalities remaining bounded | IMPLEMENTED BUT WEAKLY TESTED |
| Return with difference | consequence causally changes later decision | average authorized consequences by state/action | all v0/v1/v2 history-removal pairs | absent history restores ADVANCE | IMPLEMENTED + TESTED |
| Fail-closed uncertainty | do not invent evidence | incomplete package does not commit; disagreements stop | delayed A/B; stale records; persistent C disagreement | software waiting has no deadline; API bypass remains | IMPLEMENTED BUT WEAKLY TESTED |

The functional vocabulary is complete. Mandatory admission, representation
validation, and paired recovery are not complete across the audited interfaces.

## 3. Five-component loop audit

The normal v2 transaction uses these existing operations:

```text
package/Memory identity check
→ Memory audit and, if needed, proposed/checked record rebuild
→ Explorer action from audited records
→ bounded action-membership check
→ Map Prediction captured in PendingTransaction
→ trusted driver executes the external world once
→ A/B/C observe the same true pre-state/action independently
→ package provenance, agreement, witness and registry checks
→ inherited pair admission and predictive Measure audit
→ select valid incumbent/candidate or quarantine and propose Recovery
→ separate state authorization and Memory consistency check
→ Map/Memory/pair commit, then v2 package-ring append
→ next begin_step uses the authorized consequence history
```

On evidence disagreement, `_dispute` retains one pending transaction, increments
the sequence once, and requests re-observation. The world action is not executed
again. Persistent disagreement rejects. On a Map mismatch, the admitted
evidence grounds a Recovery proposal and the state authorizer checks it. On
Memory corruption, the retained pair decision grounds a separately checked
rebuild before Explorer use.

Concrete implicit or simplified operations:

- V0 has an explicit `ActionAuthority` checking a protected pre-state snapshot
  and Map version. V1/v2 collapse action admission into the coordinator's
  membership check and pending-transaction rules. The driver actually executes
  the action. This supports bounded actions, not v0's stronger pre-action
  ground-state guarantee; stale Map may influence an action before later repair.
- The driver supplies true pre-state/action to each evidence process. These
  world-side inputs are an explicit trusted interface, not inferred grounding.
- V1/v2 construct a Measure proposal inside `_complete_pair` and use the same
  `MeasureAuditor.expected` predicate for its initial value. This is an explicit
  comparison and injected-verdict check, not full implementation diversity
  between a separately instantiated Measure and its auditor.
- Package authorization is a control-flow precondition, not an unforgeable
  capability required by every inherited commit entry point. The facade's
  `__getattr__` exposes a route around it.
- Map/Memory/pair updates happen before the package-ring append and audit.
  Single-threaded successful calls look atomic; an exception after mutation
  does not roll back those changes. The descending-epoch case exposes this.
- Recovery attempts are counted per fresh Recovery object. The combined-fault
  case performs Memory, Measure, and state repairs in one transaction. It is
  not evidence for a global one-repair-per-transaction bound; original wording
  needs this clarification.
- Package traces do not implement every state named in v2 prose: they record
  staging and `PROCESS_VALIDATED`, while inherited traces record proposal,
  disagreement/re-observation, authorization, and rejection. Some post-call
  package trace identities use transaction zero after `pending` is cleared.
  Trace text alone is therefore not an authoritative transaction ledger.

## 4. Prediction/consequence and return-with-difference audit

`Prediction` is a frozen dataclass. In normal v0 code it is a local value created
before `environment.step`. In v1/v2, `begin_step` creates it before the driver
executes the oracle, and neither source nor Recovery rewrites it. The harness
preserves this pre-outcome snapshot independently and compares stored verdicts
with it. A stale previous Prediction is not scored as confirmation; fresh
consequence can still authorize a correctly checked recovery.

**Boundary weakness:** `PendingTransaction` is mutable and returned to the
trusted driver. Field edits to the Prediction object fail, but replacing
`pending.prediction` after outcome revelation succeeds. In 3/3 explicit driver
replacement controls, an initially wrong prediction became a stored matching
verdict. This is a real latch-integrity weakness, reported separately because
the intervention changes trusted-driver state rather than using a normal
candidate method. No independent prediction subsystem is needed to describe it.

Memory's causal dependency was established in **9/9 paired experiments**:
three versions × three identity seeds. At transaction 6, both sides had state
1, Map version 5, identical epoch/transaction coordinates and policy. With
authorized history, the next action was HOLD; after clearing only the complete
paired history (Memory and matching evidence stores), it was ADVANCE. Both
actions were then executed and committed normally.

The reason is visible in `Explorer.scores`: it averages authorized consequences
for the current state/action, uses zero for unseen actions, and breaks ties by
fixed action order. The previous state-1 ADVANCE consequence is -1, so HOLD's
unseen score 0 wins. Removing history restores the tie and ADVANCE wins. There
is no episode-position branch, randomness, test-specific policy mutation, or
oracle import in Explorer. Ignoring Memory audit instead lets an injected
positive value reverse that later choice in 3/3 negative controls.

## 5. Authority audit

Source references: [v0 runtime](../experiments/base_framework_v0/framework.py),
[v1 runtime](../experiments/base_framework_v1/framework.py), and
[v2 package facade](../experiments/base_framework_v2/framework.py).

| Mutation | Proposer | Checker / authorizer | Evidence | What stops it | Committed effect | Can proposer edit evidence? |
|---|---|---|---|---|---|---|
| Action execution | Explorer | v0 ActionAuthority; v1/v2 coordinator membership/pending gate | protected snapshot in v0; current Map/audited Memory in v1/v2 | invalid action, unavailable continuation, pending or episode bound | world executes once through trusted driver | Explorer methods receive no writable world interface; driver is trusted |
| Map update | candidate/Recovery/incumbent selector | state authorizer plus prior package admission | admitted PairDecision | mismatch, duplicate identity, invalid Recovery | new versioned MapState | Recovery receives immutable decision; cannot normally replace it |
| Measure correction | Recovery | MeasureAuditor.verify | pending Prediction plus admitted pair | wrong corrected verdict | audited match bit in pair/Memory | no normal write to pair; pending reference writable by trusted driver |
| Memory commit | coordinator record construction | CrossMemory.matches | retained admitted pair and package control flow | inconsistent record, upstream reject | bounded record/pair/package history | stored Memory is fault-injected; its protected pair is a separate trust root |
| Memory recovery | Recovery.memory_record | Memory matcher | retained pair decision | invalid rebuild or missing identity | recovered Memory slot | cannot normally edit retained pair; slot order is incorrectly reconstructed numerically |
| Recovery state commit | Recovery.state_candidate | CrossSourceStateAuthorizer | same admitted package/pair | wrong value/identity | Map and outcome record | no authority method on Recovery itself |
| Pair/package acceptance | registered evidence producers | pair/package authorizers and registry walk | A/B/C plus registry version | provenance, roles, overlap, value disagreement | admission grant, then decision retention on commit | receipts frozen; trusted driver supplies wrappers; no cryptographic origin authentication |
| Continuation | coordinator | conjunction of admission and state/record checks on intended path | successful complete transaction | rejection, pending guard, bound exception | next action permitted | generic v2 delegation exposes inherited commit path without package grant |

No claim is made that arbitrary in-process Python code cannot reach internal
attributes. That stronger isolation is not modeled. The observed public
`submit_receipt` bypass requires neither monkeypatching nor private method calls:
generic delegation makes it callable on the v2 object itself.

## 6. Provenance and self-reference audit

| Authorization path | Ultimate relation | Classification | Result |
|---|---|---|---|
| v0 snapshot/consequence | independent BoundedWorld interface | A: allowed external/protected relation | normal candidate cannot generate it |
| v1 A/B | independently written table and conditional code over world-side inputs | D: declared independent paths | identical shared corruption can still fool both |
| v2 C | separate flat relation table | D plus A | no A/B-output input; correct in alias attacks |
| v2 separation | nine-node registry | E: trusted registry root | detects registered derivation; cannot discover omitted edges |
| Map/Recovery candidate | model or correction from admitted evidence | B: candidate-derived proposal | not itself independent evidence |
| derived-witness control | C made from agreeing wrong A/B | C: shared descendant | normal registry rejects; ablated overlap check accepts |
| stored outcome reuse | pair/package decision tied to epoch/transaction | A/D mediated by E: storage and coordinator | stale coordinates blocked; chronology breaks on descending-epoch repair |

Numeric aliasing does not establish circular evidence. It exposes an invalid
comparison domain: the witness relation is injective only for declared states
and ternary consequences, while the gate accepts arbitrary integers. Correct
independent evidence cannot save a predicate that equates an invalid tuple with
a valid one. The numeric helper is imported from the witness module, but witness
generation uses its own flat table rather than that helper or the candidate.

Source process IDs are registry declarations, not authenticated attestations.
Relabeling an actually derived process as a normal path requires falsifying
trusted registration facts and remains outside the declared model. The new
numeric alias and chronology tests leave those facts intact.

## 7. Trust-root audit

| Root | Classification | Bound / candidate-control status | Attack/evidence | Completeness implication |
|---|---|---|---|---|
| World transition semantics and world-side request | ESSENTIAL EXTERNAL GROUND | fixed 4 states × 3 actions; not candidate output | independently scored finite cases | bounds the claim; not a missing component |
| A/B implementations and registered dispatch | REPLACEABLE; ESSENTIAL EXTERNAL GROUND | fixed receipts/ports; source faults injected, dispatch trusted | single-source, joint A+B faults and spoof controls | ground implementation may change without expanding minimum functions |
| C implementation | REPLACEABLE; ESSENTIAL EXTERNAL GROUND | one four-bit relation plus identity; not derived from candidate | C transient; A+B correct-C attacks; ABC control | existence of a ground route is essential; exact C implementation is not |
| Registry facts | IMPLEMENTATION CONVENIENCE; REPLACEABLE | 9 nodes, protected by model ownership and frozen records | false registry produces 3/3 false accepts | explicit trust limit, not reason to demand another registry checker |
| Pair/package/state/Memory authorizers | REPLACEABLE | finite pure comparisons plus bounded identity set | A/B/D/E ablations and alias predicate failure | trustworthy authority is an assumption; a demonstrable predicate defect is a correction obligation |
| Coordinator, epoch allocator, store ownership | IMPLEMENTATION CONVENIENCE; REPLACEABLE | one active transaction, 2 epochs, bounded rings | delegated ingress and descending-epoch API tests | trusted-code integrity does not excuse errors in unmodified public API behavior |
| Hidden oracle | TEST-ONLY | fixed finite world; absent from runtime imports | independently exposes false commits | necessary for these scores, not an added runtime component |
| Python process/host memory protection | IMPLEMENTATION CONVENIENCE; CURRENTLY UNTESTED | no hostile same-process isolation | direct trusted-driver reference replacement probe | bounds the claim; software frozen objects are not a physical security boundary |
| Physical domain separation/common causes | CURRENTLY UNTESTED | represented only by declared graph | no physical campaign | outside minimum functional completion |

Candidate-control claims are architectural ownership assumptions. Registry nodes
and mappings resist normal item mutation, but the containing Python object's
attributes are not a secure enclave. Oracle correctness and hostile code
replacement are explicitly not demonstrated by the protected tests.

## 8. Verification-regress stopping analysis

**Yes, the intended v2 trust model supports the stopping principle:** named
external evidence, registry and authorizer boundaries are outside the candidate's
modeled write authority, and a test-only oracle measures violations. The retained
ABC and registry attacks openly delimit failure beyond that boundary. It is not
necessary to add a verifier for each of these trusted roots.

**No, that principle does not establish unconditional correctness of the current
implementation.** The numeric predicate fails with those roots intact, an
exposed API omits a required gate, and a legal distinct-epoch sequence breaks
record correspondence. These are existing contract failures, not verification
regress. The appropriate next work is narrowly repairing those relationships.

## 9. Frozen stress preregistration

The [stress preregistration](minimum-framework-stress-preregistration.md) fixes
42 protected case types (including all 12 numeric-alias state/action cases),
seven paired A-G ablations, three boundary controls, and seeds 1/2/3.
It was committed before harness implementation/execution. No criterion or
coverage classification was revised after observation.

The test-only [runner](../experiments/minimum_framework_audit/run.py) records
pre-outcome predictions, executes the existing hidden oracle, constructs the
existing sources, observes runtime results, and independently checks retained
outcomes, evidence coordinates, Map truth, and ring ordering. It recomputes
registry overlap without calling the runtime validator. Exceptions after commit
are retained as failures; internal generic error counters are not the oracle.

## 10. Stress results

| Category | Executed runs | Observed |
|---|---:|---|
| Protected audit/stress | 126 | 84 pass; 42 violate covered criteria |
| Complete-framework ablation controls | 21 | 21 pass |
| Weakened variants | 21 | 15 expose forbidden effects; 6 retain downstream protection |
| Boundary/trust-root controls | 9 | 3 prediction-reference manipulations; 3 ABC false accepts; 3 registry false accepts |
| **Total** | **177** | **0 harness errors** |

The three covered failure families are:

1. **Numeric domain alias — 36/36 false accepts.** Across every existing
   state/action and all three seeds, A+B report a different valid state but a
   non-ternary consequence selected to alias correct C. For state 0 ADVANCE,
   truth is `(1,+1)`, code `3*1+(1+1)=5`. The wrong tuple `(2,-2)` also yields
   `3*2+(-2+1)=5`. Both observations agree, correct C remains 5, the normal
   registry remains unchanged, and the gate commits Map 2 and Memory -2.
   There is no range validation before encoding. Earlier frozen v2 controls
   used non-aliasing corruptions and still reproduce their published result.
2. **Delegated ingress — 3/3 commits without C.** `v2.submit_receipt("A", ... )`
   and then `v2.submit_receipt("B", ... )` resolve through `__getattr__` to
   the inherited framework. The result has `committed=True`, `continued=True`,
   one Memory/pair record and zero package decisions. This is an API authority
   leak, not a numeric false accept. The intended `submit_package` path's
   incomplete-evidence controls remain safe. A contract restricting callers to
   that path would narrow the API claim, but no such enforcement exists.
3. **Descending-epoch recovery — 3/3 paired-order failures.** Execute two
   transactions at epoch 101, then one at epoch 1 (analogously for other seeds),
   and corrupt one retained Memory consequence. Both epochs are distinct,
   positive, and accepted by `start_epoch`; no wrap or identity reuse occurs.
   Recovery sorts Memory by numeric epoch/transaction, while pair/package
   stores retain insertion order. The next transaction updates Map/Memory/pair
   and increments commits before the package audit raises an identity mismatch.
   The exception reports `commit_delta=1`: it is not a pre-commit safe rejection.

Independent short reproductions that did not import the audit harness also
confirmed the numeric-alias and delegated-API findings. Full campaign repetition
after freezing the harness produced identical case outcomes.

Combination tests for Map+Memory, Measure+stale provenance, invalid action+stale
Map, wrong Recovery+wrong epoch, imminent Memory-driven behavior, and all four
independent fault injections behaved safely within their preregistered
expectations. Success of these particular combinations is not universal
multi-fault coverage.

## 11. Temporal consistency results

| Case | Outcome across three seeds |
|---|---|
| Earlier authorized package replayed later | 3/3 safe rejects |
| Old Prediction before new execution | 3/3 not confirmed; true outcome correctly recovered |
| Old A consequence after Map version/transaction advances | 3/3 bad rounds rejected; fresh rounds commit |
| New epoch with reused transaction number and old package | 3/3 old epochs rejected; fresh package commits |
| Evicted Memory record reinserted into a current slot | 3/3 identity guards halt before policy use |
| Duplicate delivery after commit | 3/3 no pending transaction; no duplicate commit |
| Old delayed B after later transactions progress | 3/3 bad rounds rejected; fresh retry commits |
| Eight-entry ring eviction after Memory repair | 3/3 aligned eviction with eight entries |
| Distinct decreasing epochs plus Memory repair | 3/3 ring-order failures after a later commit |

Numeric monotonicity of epochs is an implicit recovery assumption, absent from
`start_epoch`'s explicit contract, which requires only difference and a two-epoch
bound. Epoch identifiers are not timestamps. The temporal Map-version test also
changes transaction identity; it does not prove protection against a trusted
coordinator modifying the Map version inside one pending transaction. The
pending version is recorded but not independently checked at commit.

Delayed partial evidence blocks new `begin_step` calls and produces no new
history. The software has no clock/timeout; no claim of bounded waiting time was
tested. The separate RTL authorization gate's timeout remains independently
covered by its own regression. Identity wrap and concurrency remain out of scope.

Observed cardinality maxima at harness observation points: Memory/pairs/packages
8 each; staged items 3; Map quarantine 1; package and inherited trace 24 each;
external trace 12 of the allowed 24. Memory quarantine is transient inside a
synchronous repair and is empty when the harness observes successful returns;
its one-entry guard was inspected, not mistaken for an observed occupancy peak.
Finite cardinality does not imply correct paired ordering.

## 12. Ablation and negative-control results

All seven normal counterparts passed across three seeds. The weakened variants
are isolated test code; normal runtime files and future instances are untouched.

| Ablation | Outcome | Interpretation |
|---|---|---|
| A Ignore provenance at package and inherited pair gates | 3/3 stale packages accepted into current authorization | identity checks prevent real temporal crossover |
| B State proposer self-authorizes | 3/3 wrong Recovery states reach Map | independent state recheck matters |
| C Ignore Memory audit | 3/3 corrupt history changes imminent HOLD to ADVANCE | causal history is useful only when audited |
| D Accept descendant overlap | 3/3 derived-witness wrong packages commit | numeric agreement cannot replace declared separation |
| E Always propose incumbent as selected | 3/3 safely rejected by retained downstream state gate | redundant protection survives this isolated removal |
| F Skip Map quarantine | 3/3 invalid recoveries still rejected downstream | tested stopping does not alone establish quarantine's necessity |
| G Permit inherited commit before package completion | 3/3 commits despite bad C and absent package grant | v2 gate is necessary but currently bypassable |

E changes only selection policy in a test-local adapter and preserves the state
check; it does not remove a second gate merely to force failure. F tests only
the selected invalid-recovery schedule. Neither proves that incumbent policy or
quarantine can be removed generally.

The separate boundary controls reproduced ABC and corrupted-registry false
accepts (3/3 each), plus manufactured prediction confirmation after trusted-driver
reference replacement (3/3). These nine runs are not counted in the 42 covered
violations or 36 protected numeric false accepts.

## 13. Falsification table

| Frozen criterion | Observation | Verdict |
|---|---|---|
| F1 Protected false accept | 36 alias runs commit wrong Map and Memory with correct C | FAIL |
| F2 Unauthorized history | 3 package-less API commits; alias input validity also violated | FAIL |
| F3 Duplicate authorization/commit | none in covered duplicate/epoch tests | PASS in tested scope |
| F4 Invalid Recovery authorization | deliberately wrong Recovery rejected normally; ablated self-authorization fails | PASS for honest admitted evidence; F1 still defeats recovery ground |
| F5 Provenance crossover | stale coordinate tests pass; pair chronology assessed separately as F8 | PASS in tested coordinate scope |
| F6 Continuation before gates | delegated receipt API grants continuation without package | FAIL |
| F7 Corrupt Memory influences Explorer | normal audit repairs before use; audit ablation changes action | PASS in tested cases |
| F8 Bound or paired-rotation failure | 3 descending-epoch misalignments; 3 package-less histories | FAIL for paired structure; tested size limits hold |
| F9 Post-outcome fabricated confirmation | no normal candidate path observed; mutable driver reference permits it | BOUNDARY WEAKNESS; not a protected counterexample |
| F10 Memory not causally effective | all 9 history-removal pairs restore original action | PASS |
| F11 Invalid incumbent retained as valid | normal valid-ground selection cases pass; false evidence acceptance remains F1 | PASS conditional on valid admitted evidence |
| F12 Declared recovery cannot recover | 3 single-record repairs break cross-epoch ring correspondence | FAIL |

Criteria can overlap in the same run. The total 42 is a count of distinct
covered runs, not the sum of all criterion hits. No criterion was weakened or
runtime patched after these failures.

## 14. Original-framework requirement coverage

The original sequence ACT → OBSERVE → PRESERVE → DETECT → LOCALIZE → RESTRICT →
CORRECT → VERIFY → UPDATE → CONTINUE is implemented. Return with difference is
causal, not a scripted episode marker. Evidence is separated from candidate
generation, correction remains a proposal, and authorized history survives
ordinary bounded rotation.

What remains is enforcement of three already-required relationships: admitted
numbers must belong to the relation's domain; every reachable commit ingress
must require the intended package grant; and a recovered record must preserve
its paired temporal identity. These are original minimal obligations. More
world states, exploration sophistication, or external verifiers would not fix
them automatically.

The v0 single-ground loop already demonstrates the original functional skeleton.
The later evidence extensions add defenses and assumptions; they are not proof
that the skeleton required infinitely many layers. Published narrow results
remain valid for their frozen scenarios, while the new stress cases expose
limits outside those specific schedules but inside these audit obligations.

## 15. Post-minimum extensions

| Idea | Classification | Reason |
|---|---|---|
| Longer-term trace/accountability | POST-MINIMUM EXTENSION | bounded transaction association is core; unlimited retention is not |
| Longer-horizon prediction | POST-MINIMUM EXTENSION | one-step pre-outcome prediction already supplies the minimal relation |
| Inferred causal independence | POST-MINIMUM EXTENSION | declared, attackable external boundaries suffice for this scope |
| Dynamic trust scores | POST-MINIMUM EXTENSION | no frozen obligation requires adaptive source ranking |
| Larger worlds | POST-MINIMUM EXTENSION | may test transfer; cannot cure current acceptance predicate defects |
| Additional checkers/sources/witnesses | POST-MINIMUM EXTENSION | existing gate enforcement is the immediate problem |
| Adaptive source diversity | POST-MINIMUM EXTENSION | extends the trust model rather than completing the bounded loop |
| Lossless trace packing, smaller records, faster RTL | EFFICIENCY / SCALING ONLY | resource efficiency is distinct from the demonstrated contract failures |
| Domain-valid admission and mandatory gate enforcement | CORE REQUIREMENT | already needed for sound independent recheck and authorization |
| Identity-preserving Memory repair | CORE REQUIREMENT | required to reuse authorized consequence without temporal contamination |

## 16. Software ↔ RTL mapping status

| Minimum function | Existing Horus support | Current complete-loop status |
|---|---|---|
| Action sequencing / Explorer | controller, routing, valid/ready interfaces | Memory-scored three-action policy is software-only |
| Map state and prediction | state registers, arithmetic models, keeper state | four-state revisable Map/predictor is software-only |
| Measure comparison | comparators, Rule-5/SKPR local detection, independent numerical specification | framework consequence relation is software-only |
| Memory/provenance | buffers, protected records, transaction/epoch checks | eight-entry outcome/pair/package rings are software-only |
| Recovery and quarantine | replay wrapper, bounded quarantine and protected-source gate | five-component recovery coordinator is software-only |
| Independent authorization | `experiments/bounded_commit` RTL and testbenches | implemented and simulated for that numerical task, not full v2 |
| Process registry and C | naturally map to small ROM/table and comparator interfaces | proposed mapping only; no v2 RTL implementation |
| Failure/continuation gating | backpressure, commit signals, bounded gate timeouts | full package conjunction is software-only |

Current evidence consists of RTL simulation, software experiments, and previously
reported synthesis/mapped estimates where applicable. It does **not** establish
fabricated silicon, FPGA deployment, physical fault testing, placed/routed
timing, or full-loop hardware feasibility. This audit performs no synthesis or
hardware optimization. The existing [mapping](../docs/HARDWARE_FRAMEWORK_MAPPING.md)
is retained unchanged and remains a proposal for complete-loop RTL.

## 17. Remaining limitations and regression preservation

- Coverage is deterministic, finite, and identity-repeated. It is not a
  statistical reliability estimate or exhaustive arbitrary fault proof.
- The numeric attacks alter receipt integers, not the world. Original v2
  attacks deliberately kept their replacement consequence ternary; this audit
  tests the previously unchecked domain boundary. It does not rewrite the
  earlier 57-scenario PASS.
- The facade bypass matters to an all-public-ingress contract. A deployment
  strictly restricted to `submit_package` avoids that route but still has the
  numeric-alias and cross-epoch recovery defects.
- Decreasing distinct positive epoch IDs are accepted by the code; an external
  monotonic-epoch restriction would narrow coverage, but was not in its contract.
- No software timeout, concurrent mutation protection, physical independence,
  malicious-oracle defense, or hostile Python-process isolation is claimed.
- Identity/Map-version/Prediction ownership relies partly on the trusted driver.
  The frozen object does not freeze its containing mutable reference.
- Multiple fresh Recovery objects make aggregate attempt wording ambiguous.
  This audit reports the actual repairs and does not call one-per-object a
  global transaction budget.
- Scalar traces are observational, not complete proofs of authority. The test
  harness records external event/receipt/prediction evidence separately.

Fresh preservation regression, actually executed on this audit tree:

| Command | Observed result |
|---|---|
| `make test` | 53/53 core steps pass |
| `make independent-commit` | 4,200 protected transactions; retained 300 negative-control false accepts |
| `make independent-commit-followup` | 2,700 broader-fault transactions; 21 trace comparisons |
| `make base-framework-v0` | 12 tests / 42 scenarios pass |
| `make base-framework-v1` | 10 tests / 69 scenarios; retained 3 common-mode false accepts |
| `make base-framework-v2` | 13 tests / 57 scenarios; retained 3 ABC and 3 registry false accepts |

These passing regressions coexist with the newly failing stress campaign. All
runtime files, prior experimental summaries, and historical reports are
byte-for-byte preserved relative to the public checkpoint.

## 18. Narrowest defensible conclusion

The minimum framework's functional loop is present, including causally effective
authorized Memory and checked correction proposals. Its existing enforcement is
not complete under the frozen audit scope: correct independent evidence can be
defeated by an unchecked representation domain, mandatory package authorization
can be bypassed through a public delegated method, and permitted epoch ordering
can break paired Memory recovery after commit. These observed failures justify
core corrections without adding architecture.

## 19. Recommendation

**B — CORE CORRECTION REQUIRED.** Do not proceed to broader-domain, scaling, or
new-checker work as though the current audit passed. This finding does not
imply that the framework needs another component or that explicit roots of trust
make minimum completion impossible.

## 20. Smallest next correction/experiment — not implemented

The next authorized work should be a bounded correction of existing boundaries:

1. Validate the existing state/consequence domains before applying the current
   witness encoding. Re-run all 12 clean world transitions and the 12 alias
   cases per seed; invalid tuples must be rejected with unchanged correct C.
2. Make the current package gate mandatory at every exposed v2 commit ingress.
   Re-run direct A/B delivery without C as well as the normal full-package path.
3. Preserve the recovered record's paired slot/identity rather than infer order
   from numeric epoch values; validate correspondence before commit becomes
   visible. Re-run descending/increasing epoch and full-ring repair cases.

Resolve Prediction-reference ownership and aggregate Recovery-attempt wording
explicitly in the existing contract. The smallest prediction experiment is the
already retained before/after-reference probe with an enforced ownership/latch
contract, not a new predictor or another truth source.

No fixes, v3 implementation, source/witness additions, world enlargement, hardware
optimization, main modification, tag changes, or push were performed. This audit
stops with reproducible failures and the bounded correction recommendation.
