# Minimum-framework repair 1 results

**A — MINIMUM FRAMEWORK COMPLETE FOR DECLARED SCOPE.** All 126 protected
frozen-campaign runs passed, with zero protected violations and zero harness
errors. All 109 direct repair checks and all six historical regression commands
passed. Architecture development stops at this evaluation.

## 1. Baseline and preservation

Audit baseline: `412de7bb02a4cedfab5d648debffe54b8b5a94bb`,
`research/minimum-framework-audit`. Its checkout was clean before creating
`research/minimum-framework-repair-1`. Public main remains
`b8e4245ef14b11ee5d94ce851aec4d8dc059963f`.

The repair preregistration was committed as `304ec9f` before runtime edits.
Domain/authority repair is `bb1c54c`, identity/transaction staging `3cf1f93`,
and prediction ownership `6a8789a`. No main, tag, or remote was changed.
The frozen audit harness, completion definition, stress preregistration,
audit report/results, and historical v0/v1/v2 results are byte-identical to
the audit baseline. Historical claims remain scoped to their original commits;
their source hashes are not relabeled as hashes of the repaired runtime.

Reproduce with the [repair runner](../experiments/minimum_framework_repair_1/README.md).
Public compact evidence: [results.json](../experiments/minimum_framework_repair_1/results.json).
Fresh regression execution: [regression.json](../experiments/minimum_framework_repair_1/regression.json).
Full campaign SHA-256:
`529e13b97f51e23126fc099352d26800e458c30257afeae4c80841772d5e3ba4`.
Raw traces/logs are retained outside the public tree. The compact evidence
includes runtime, harness, and frozen-criterion source hashes.

## 2. Exact code changes

Only two runtime files changed:

* `experiments/base_framework_v2/framework.py`: domain admission, explicit
  diagnostic delegation, fail-closed legacy ingress, package-required inner
  admission, bounded state staging, and prepublication three-ring identity checks.
* `experiments/base_framework_v1/framework.py`: original-slot Memory recovery,
  a v2-enabled package-grant guard, and private pre-outcome prediction ownership.

The new repair experiment contains test adapters, direct checks, reproduction
instructions, and new evidence. README and the public manifest identify this
checkpoint. No world, action, source, witness, checker component, learning
mechanism, or RTL implementation was added. C's independent implementation and
relation encoding are unchanged; v0 runtime is unchanged.

## 3. Numeric-domain repair

The existing package authorizer rejects non-integer/bool/float or out-of-domain
state/consequence values before encoding/comparing. Both receipts must have
pre/next states in 0..3, an existing action, and a consequence in -1..1.
C must contain an integer relation code in 0..11. Registry and provenance
validation then continue normally. The multiplier remains 3.

All 12 legitimate world transitions commit correctly. The 36 alias packages
reject; 36 additional small boundary probes cover pre/next state -1/4,
consequence -2/+2, C -1/12, invalid action, and representative bool/float aliases.
Each invalid probe checks both available rounds, no continuation, and unchanged
Map/Memory/pairs/packages/authorization ledger. This is finite direct coverage,
not an arbitrary-input fuzzing claim.

## 4. Mandatory authorization and ingress review

Generic inherited-method delegation is removed. The explicit `submit_receipt`
compatibility method rejects and withdraws continuation. The inner coordinator
also requires a package grant at receipt admission and pair completion when
used by v2. The grant binds epoch, transaction, round, and both observation IDs.
It exists only on the staged candidate after successful package admission and
is cleared before publication and on all transaction exits.

| Public method | Access | Package grant required? | Can publish a new world transaction? | Verified result |
|---|---|---|---|---|
| `begin_step` | mutating proposal / retained-history repair | retained package/pair identity for repair; no fresh grant yet | no | validates repair before proposal visibility; no continuation while pending |
| `start_epoch` | mutating bounded lifecycle reset | no new evidence transaction | no | existing two-epoch contract retained |
| `observation_request` | read-only | no | no | returns current request coordinates |
| `stage` | mutating bounded evidence staging | no | no | only three registered roles; partial evidence cannot commit |
| `submit_receipt` | mutating rejection control | fresh package mandatory, unavailable here | no | explicit fail-closed result for A and B |
| `submit_package` | mutating transaction | yes, for current identity/round | yes | commits only after all mandatory checks |
| `assert_bounds` | read-only validation | no | no | existing logical limits enforced |

The seven-method inventory is checked directly. No inherited private completion,
dispute, or recovery method is delegated. Diagnostic `inner` access remains for
research fixtures: its `submit_receipt` is also tested and blocked without a
grant. Its other public methods are lifecycle/proposal/request/bounds methods,
not alternative pair commit ingresses. Mutable diagnostic objects and deliberate
assignment to private flags/code are trusted-process access, not a security
sandbox. The ablation deliberately uses that access and is labeled accordingly.

## 5. Memory identity and order

Recovery captures insertion order, finds one exact
`(epoch, transaction_id, pair_decision_id)` slot, verifies its paired slot,
constructs a Recovery proposal, and independently checks it with the existing
Memory matcher. Only that slot is replaced. No identity sorting remains on the
repaired v1/v2 path.

V2 validates equal ring lengths, unique record identities, Memory/pair identity
equality, and package/pair epoch, transaction, round, and observation bindings.
These checks surround staged retained-history recovery and precede publication
of a newly authorized transaction. Epoch is an identity, not a timestamp.

## 6. Atomic publication

The existing bounded inner state is copied for proposal/recovery preparation
and for package completion. Map, Memory, pair rotation, authorization ledger,
and commit counters mutate on the staged copy. Proposed packages and staged
rings are checked before publishing the coordinator and package list.
Ordinary rejection publishes control/diagnostic changes only. An exception at
final validation withdraws continuation and leaves authorized state unchanged.

Eight direct probes inject final-check failure, wrong package identity, wrong
pair identity, and package-length mismatch at both zero and eight retained
records. Every probe observes **commit_delta = 0**, unchanged Map (including
version/validity), Memory, pair/package rings, authorization ledger, eviction
count, and quarantines. The full-ring probes include an attempted rotation.

Retained Memory correction is a separate pre-action operation: it is staged,
validated against already authorized paired history, then made available to
Explorer. New-outcome publication is staged again. Neither operation publishes
before its mandatory correspondence check. There is no general database or
concurrency protocol: publication assumes the declared single-threaded runtime.
Each logical ring remains bounded at eight. Staging temporarily retains a
second bounded coordinator copy and a bounded proposed package list; it is not
a claim that physical storage still costs exactly one eight-entry ring.

## 7. Prediction ownership

`begin_step` privately retains the frozen Prediction returned by Map. Measure
evaluation and Recovery remeasurement use this snapshot, not the externally
replaceable `pending.prediction` reference. All three original replacement
probes commit the valid correction while recording **no manufactured
confirmation**; all three direct repetitions pass. Prediction fields remain
frozen. This hardens ownership without claiming hostile-process isolation.

The stale-prediction protected scenario still supplies the same old model
output, now at the pre-outcome producer before latching. F9 observes the
prediction actually used and still checks confirmation against independent truth.

## 8. Recovery budget

`RECOVERY_LIMIT = 1` applies per fresh Recovery object. The existing coordinator
can instantiate one for retained Memory repair, one for Measure repair, and one
for Map/state repair during one transaction: **at most three recovery proposals,
one per subsystem**, not one total. The combined direct probe measured exactly
1 + 1 + 1 and a successful independently checked commit. There is separately
at most one evidence re-observation (two receipt rounds). It is not an extra
Recovery object. Recovery was not redesigned.

## 9. Frozen campaign totals

| Category | Executed | Pass / no violation | Violation | Harness errors |
|---|---:|---:|---:|---:|
| Protected audit/stress | 126 | 126 | 0 | 0 |
| Complete-framework ablation controls | 21 | 21 | 0 | 0 |
| Weakened variants | 21 | 6 | 15 | 0 |
| Boundary controls | 9 | 3 | 6 | 0 |
| Total frozen scenario runs | 177 | 156 | 21 | 0 |
| Additional direct checks | 109 | 109 | 0 | 0 |

The prior 84 passing protected runs remain passing. All 42 previously failing
protected runs now pass. The historical 177-run result is unchanged. The
repair-local adapter preserves scenario identities, seeds, the hidden oracle,
and falsification criteria. Its three explicit interface changes are documented
in the runner README; no negative result was removed to obtain A.

## 10. Alias results

**36/36 safe rejections**, covering all four states × three actions × three
seeds. Direct repeated checks verify zero authorized-state mutation after each
invalid package round, including unchanged version, ledger, and ring contents.
Correct C is neither replaced nor derived from the invalid A/B proposals.

## 11. Delegated-ingress results

**3/3 frozen legacy-ingress runs blocked**. Six direct endpoint probes (three
facade and three inner) each attempt A and B without C and observe no commit,
no continuation, and no authorized-state mutation. Normal package submission
passes all 12 legitimate transitions and the historical v2 campaign.

## 12. Descending-epoch results

**3/3 frozen descending-epoch recoveries pass** with aligned rings. The direct
epoch-101, epoch-101, epoch-1 schedule reproduces retained corruption, verifies
same-slot recovery before new commit, then successfully commits the following
transaction. Reusing transaction number 1 under a distinct epoch is preserved
as a distinct identity.

## 13. Temporal consistency

Six direct schedules cover increasing 1→101 and decreasing 101→1 identities,
with 2, 8, and 9 initial commits. They include full rings, recovery just before
eviction, and recovery after rotation. Each successful commit checks insertion
order across Memory, pairs, and packages; the following transaction also passes.
The frozen campaign additionally passes old package replay rejection, stale
epoch recovery, delayed partial evidence, delayed old B, duplicate delivery,
evicted-history reinsertion, and the one-retry boundary. No monotonic epoch
assumption or new timer was introduced.

## 14. Memory causality

All **9/9 paired experiments** (v0/v1/v2 × seeds 1/2/3) retain the same
pre-decision nonhistory inputs. Authorized history selects **HOLD**; removing
that history selects **ADVANCE**. Enforcement repair preserves the frozen
return-with-difference property.

## 15. Authority ablations

| Removed/weakened invariant | Complete controls | Weakened results |
|---|---|---|
| Evidence provenance coordinates | 3 safe | 3 stale-evidence violations |
| Independent state authorization of Recovery | 3 safe | 3 wrong-state/self-authorization violations |
| Memory audit before behavior | 3 safe | 3 corrupt-history/action violations |
| Descendant/shared-path separation | 3 safe | 3 false accepts/provenance violations |
| Incumbent selection | 3 safe | 3 safe stops: independent state gate still rejects |
| Quarantine | 3 safe | 3 safe stops: independent state gate still rejects wrong Recovery |
| Mandatory package gate before continuation | 3 safe | 3 package-less commits/continuations |

The last weakening explicitly removes the repaired ingress guard in a test-local
adapter. No new runtime bypass is shipped. Other weakening implementations are
unchanged. The six safe weakened runs show redundancy in these schedules; they
do not prove that incumbent policy or quarantine is universally unnecessary.

## 16. Fresh historical regressions

All commands below executed on the repaired runtime and returned exit code 0.

| Command | Fresh measured result |
|---|---|
| `make test` | 53 executed steps passed |
| `make independent-commit` | 21 schedules, 4,200 protected transactions; 300 expected negative-control false accepts |
| `make independent-commit-followup` | 2,700 broader-fault transactions; 21 paired trace comparisons passed |
| `make base-framework-v0` | 12 tests / 42 scenarios; zero protected false accepts, false rejects, duplicate authorizations |
| `make base-framework-v1` | 10 tests / 69 scenarios; zero protected false accepts; 3 common-mode false accepts |
| `make base-framework-v2` | 13 tests / 57 scenarios; zero protected false accepts; 12 A+B common-mode blocks; 3 A+B+C and 3 corrupted-registry false accepts |

The v2 twelve blocks comprise six correct-C and six differently-corrupted-C
cases. They are not twelve correct-C observations. Fresh logs and full outputs
remain external; their hashes and compact execution record are public. No
historical result file was overwritten.

## 17. Frozen falsification criteria

| Criterion | Repaired observation | Verdict |
|---|---|---|
| F1 Protected false accept | zero in 126 protected runs; boundary/ablated false accepts retained | PASS within model |
| F2 Unauthorized history | invalid domain and package-less ingress publish no history | PASS |
| F3 Duplicate authorization/commit | replay/duplicate/epoch tests retain unique identities | PASS |
| F4 Invalid Recovery authorization | wrong proposal rejected by independent gate | PASS |
| F5 Provenance crossover | stale coordinates and descendant paths rejected normally | PASS |
| F6 Premature continuation | no grant from partial, invalid, or legacy ingress | PASS |
| F7 Corrupt Memory changes behavior silently | repair before Explorer; removal of audit still exposes violation | PASS |
| F8 Bounds and ring pairing | chronological alignment, rotation, and existing limits hold | PASS |
| F9 Manufactured post-outcome confirmation | replaced external reference cannot replace latched prediction | PASS in tested ownership boundary |
| F10 Memory has no causal effect | all nine history-removal pairs restore ADVANCE | PASS |
| F11 Invalid incumbent retained | independent state check survives selection weakening | PASS |
| F12 Declared recovery fails | all descending and direct temporal recoveries succeed | PASS |

## 18. Remaining trust roots

The fixed process registry must truthfully describe the registered evidence
paths. The covered independence model assumes C remains an independent valid
reference for the tested A+B corruption; path declarations do not prove physical
independence. Simultaneous matching A+B+C corruption still causes **3/3**
out-of-model false accepts, and a false trusted registry causes **3/3**.
These negative results remain visible in both the frozen-boundary rerun and
the fresh v2 regression.

Other roots are the trusted single-threaded coordinator, authentic identity
and bounded no-wrap lifecycle, protected retained paired evidence, code/registry
integrity, and the test harness's separate world/oracle for measuring truth.
Mutable Python diagnostic objects are not isolated against arbitrary trusted
code replacement. No physical hardware validation, common-mode immunity,
general grounding, or arbitrary causal-independence result follows.

## 19. Existing fourteen-function completion decision

The existing completion definition is unchanged. Each row below is
**IMPLEMENTED + TESTED** within the declared roots and campaign.

| Frozen function | Evidence |
|---|---|
| 1. Explorer proposes bounded actions | clean loops, invalid-action rejection |
| 2. Map is revisable and separate from truth | corrupted Map recovery, independent oracle checks |
| 3. Measure compares prediction and outcome | stale/wrong Measure tests and latched prediction probes |
| 4. Memory retains authorized causal history | ring/provenance checks and nine causal pairs |
| 5. Recovery proposes bounded correction | wrong proposals rejected; three-subsystem budget measured |
| 6. External consequence route | unchanged independent A/B/C production paths and descendant controls |
| 7. Proposal differs from authorization | mandatory package grant and self-authorization ablation |
| 8. Evidence binds transaction/state/epoch/source | admission, aliases, stale/replay/descending identities |
| 9. Failure withdraws continuation | persistent disagreement, invalid domain, and legacy rejection |
| 10. Recovery waits for independent recheck | wrong Recovery rejection; final-check atomicity |
| 11. Valid incumbent may survive | retained valid incumbent, invalid incumbent/selection controls |
| 12. State/retry/trace bounds | full rings, eviction, quarantine, two-epoch and one-retry guards |
| 13. Return with difference | HOLD with history / ADVANCE without, 9/9 pairs |
| 14. Insufficient evidence may stop | partial wait, retry exhaustion, no fabricated confirmation |

**Decision A — MINIMUM FRAMEWORK COMPLETE FOR DECLARED SCOPE.** No remaining
demonstrated protected contract failure requires a correction under these frozen
criteria. This is not an exhaustion of possible faults or a proof over arbitrary
Python inputs. Architecture development stops; no v3 is proposed or implemented.

## 20. Narrowest defensible conclusion

The existing five-component framework functions together under its bounded
declared model after domain admission, mandatory authorization, identity-aligned
publication, and prediction-ownership repairs. It survives the frozen covered
stress campaign and fresh historical regressions, preserves causal Memory
influence, and still exposes the declared trust-root failures. No broader truth,
universal fault-tolerance, self-improvement, AGI, or physical-hardware claim is
made. Main and tags remain unchanged; nothing was pushed.
