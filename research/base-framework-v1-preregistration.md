# Base framework v1 cross-source pre-registration

**Status:** frozen before implementation and execution, 2026-09-18.

**Parent milestone:** Base Framework v0 commit
`6752f0adf591bf6ceacfe4b07cee967075f49c20`. The parent source and measured
results are immutable inputs to this branch.

## Research question

Can the unchanged four-state Explorer/Map/Measure/Memory/Recovery loop require
two structurally separate, provenance-matched observation channels, withhold
commit while evidence is incomplete, recover from one transient channel fault
through one re-observation, and stop rather than guess when independent evidence
remains insufficient?

This experiment moves the declared trust boundary from one protected receipt to
a registered pair. It does not eliminate trust, prove causal independence, or
establish that two agreeing sources are true.

## Frozen world and component scope

The v0 world is unchanged: states `{0,1,2,3}`, actions
`{ADVANCE,HOLD,RETREAT}`, the same 12 transition/consequence cases, the same
deterministic Memory-scored Explorer, one versioned Map incumbent, predictive
Measure semantics, eight outcome records, and one-attempt Recovery.

The runtime framework cannot import or access the hidden test oracle. The
campaign driver alone executes the oracle, passes only the transaction envelope
to registered observation channels, and later uses oracle truth to score the
framework decision.

## Exact source contracts

The only shared source data type is an immutable `SourceReceipt` with:

`epoch, transaction_id, observation_id, source_id, channel_sequence,
pre_state, action, observed_next_state, observed_consequence, lineage_class,
fault_domain`.

| Contract | Source A | Source B |
|---|---|---|
| Input | Transaction envelope: epoch, transaction, pre-state, action, observation round | Same fields, separately supplied |
| Implementation | Explicit 12-entry table | Independently written conditional/arithmetic rules |
| Source identity | Constant `SOURCE_A`, set inside A | Constant `SOURCE_B`, set inside B |
| Fault domain | Constant `OBSERVATION_A`, set inside A | Constant `OBSERVATION_B`, set inside B |
| Sequence | 0 initial, 1 re-observation | 0 initial, 1 re-observation |
| May propose | Its own immutable observation | Its own immutable observation |
| May authorize | Nothing | Nothing |
| Forbidden | Calling/importing B, copying B, candidate-selected identity | Calling/importing A, copying A, candidate-selected identity |

The source modules share only the frozen immutable receipt/envelope types. They
do not share transition helpers, observation helpers, or receipt constructors.
The source registry binds a concrete object/port to its expected identity and
fault domain outside candidate data.

## Hidden oracle

The test-only oracle owns the true world state and a third implementation of the
12-case transition relation. It returns truth only to the campaign driver. The
driver supplies pre-state/action transaction inputs to the observation ports;
oracle next-state/consequence never enter Explorer, Map, Measure, Memory,
Recovery, the pair authorizer, or runtime coordinator.

External scoring compares every commit/rejection with oracle truth and an
independently retained driver trace. It recomputes result class and structural
pair validity without trusting runtime metric counters.

## Provenance and fault-domain model

The pair identity is `(epoch, transaction_id, pair_decision_id)` and each member
also binds `(observation_id, source_id, channel_sequence, pre_state, action,
lineage_class, fault_domain)`.

Accepted pairs require registered ports A and B, exact identities, equal epoch,
transaction, sequence, pre-state, and action, different observation IDs,
distinct allowed fault domains, `EXTERNAL_OBSERVATION` lineage on both, and
agreement on next-state and consequence. A name in a receipt does not establish
source identity; the registry/port binding does.

Lineage classes are `EXTERNAL_OBSERVATION`, `DERIVED_SOURCE`, and
`SHARED_ANCESTOR`. Fault domains are `OBSERVATION_A`, `OBSERVATION_B`, and
`SHARED_OBSERVATION`. These are declared structural labels, not proof about
physical independence or hidden common causes.

## Authority and disagreement policy

Authority states used are `PROPOSED`, `OBSERVED_PARTIAL`, `OBSERVED_PAIRED`,
`DISAGREEMENT`, `REOBSERVING`, `MEASURED`, `QUARANTINED`, `RECOVERING`,
`AUTHORIZED`, and `REJECTED`.

| Transition | Who may produce it | Who authorizes it |
|---|---|---|
| Proposal → action execution | Explorer | v0-style ActionAuthority from current Map/envelope |
| First receipt → partial | Registered source port | Coordinator records only; no commit authority |
| Complete pair → paired/disagreement | Pairing coordinator | CrossSourceAuthorizer validates both ports, provenance, domains, lineage, and agreement |
| Disagreement → re-observing | Coordinator | Fixed policy permits exactly one new observation round |
| Paired → measured | Measure | Separate MeasureAuditor recomputes prediction/observation verdict |
| Quarantined state → recovery candidate | Recovery | CrossSourceStateAuthorizer checks candidate against authorized pair decision |
| State/Memory staging → commit | Map/Memory coordinator | State and Record authorizers; both must pass before atomic commit |
| Commit → continuation | Coordinator | Only after complete pair, measurement audit, state authorization, and Memory authorization |

Incomplete evidence causes no Map or Memory commit. Invalid/mismatched evidence
enters one transaction quarantine and requests one re-observation. If round 1
forms an authorized pair, processing resumes. If round 1 remains incomplete or
invalid, the transaction is safely rejected and continuation stops. Neither A
nor B is chosen as truth during disagreement.

Late round-0 evidence cannot overwrite or supplement a round-1 decision.
Duplicate A cannot occupy B's registered port. Recovery cannot choose a source,
edit or fabricate receipts, or authorize its own candidate.

## Frozen bounds

| Resource | Maximum |
|---|---:|
| World states / actions | 4 / 3 |
| Source channels | 2 |
| Receipts per observation round | 2 |
| Observation rounds per transaction | 2 (initial + 1 re-observation) |
| Re-observation attempts | 1 |
| Pending/quarantined transactions | 1 |
| Map | 1 incumbent + 2 candidates |
| Memory / authorized pair decisions | 8 / 8 |
| Recovery candidates / attempts | 1 / 1 |
| Episode transitions | 12 |
| Epochs per scenario | 2 |
| Runtime trace records | 24 |
| Driver audit records | 24 |
| Authorization identities per epoch | 24 |

One recovery attempt means zero recovery retries. Any unplanned growth or silent
eviction outside the paired eight-entry rings fails the experiment.

## Frozen scenarios and expected outcomes

Each scenario runs for epoch seeds 1, 2, and 3. Seeds vary identity, not random
behavior.

| Scenario | Expected protected outcome |
|---|---|
| Clean dual-source episode | 12 commits; later state-1 action changes `ADVANCE → HOLD` |
| A transient corruption | Initial disagreement, one re-observation, correct commit/continue |
| B transient corruption | Symmetric successful recovery |
| A persistent corruption | Two disagreements, safe reject, no commit |
| B persistent corruption | Symmetric safe reject |
| Stale A / stale B sequence | Reject initial evidence; one valid re-observation may recover |
| Wrong epoch A / B | Reject, re-observe once, then stop if fault persists |
| Wrong transaction A / B | Reject, re-observe once, then stop if fault persists |
| Delayed second receipt | Partial state only after A; no commit; commit after valid B arrives |
| Duplicated A receipt | Never count as A+B; persistent incompleteness safely rejects |
| Source-ID spoof | Port/registered identity check rejects; persistent spoof stops |
| Derived B from A | Naive equality agrees; real authorizer rejects as non-independent |
| Declared shared ancestor | Numerical agreement; real authorizer rejects lineage/domain |
| Wrong Measure verdict | Auditor detects; one independently recomputed correction may commit |
| Corrupted Memory | Audit before Explorer use; rebuild only from authorized pair decision |
| Invalid state recovery | Wrong candidate rejected; no commit/continuation |
| Valid incumbent vs bad candidate | Retain verified-valid incumbent |
| Stale incumbent | Quarantine; recover only from authorized pair decision |
| Epoch transition | Old evidence rejected; fresh pair can proceed in epoch 2 |

## Out-of-model negative controls

1. **Common mode:** both registered channels emit the same wrong next-state and
   consequence while retaining apparently valid separate metadata. The pair
   gate may show structural false confidence. The full v0 Measure/Map check is
   still expected to reject because the wrong pair disagrees with the unchanged
   independent prediction. The oracle will score the actual outcome. Any false
   commit is reported as `OUT_OF_MODEL_COMMON_MODE_FAILURE`, prominently and
   separately from the protected single-channel claim.
2. **False independence:** a copied/derived B agrees with A. A naive equality
   checker must agree; the real authorizer must reject B's lineage/port origin.
3. **Shared ancestor:** two numerically agreeing receipts declare a shared
   ancestor/domain. The real authorizer must reject them.

These controls do not prove safety from hidden common causes. A zero common-mode
false-accept count would only show that the unchanged Map/Measure check caught
the injected pattern.

## Frozen result classes and metrics

Result classes are `SAFE_AUTHORIZATION`, `SAFE_REJECTION`,
`SUCCESSFUL_RECOVERY`, `FALSE_ACCEPT`, `FALSE_REJECT`, and
`OUT_OF_MODEL_COMMON_MODE_FAILURE`.

The campaign reports clean authorizations, protected false accepts, false
rejects, duplicate authorizations, single-source disagreements,
re-observations, successful re-observation recoveries, persistent-disagreement
rejections, provenance and source-identity rejections, derived-source and
shared-ancestor rejections, invalid-recovery rejections, Measure and Memory
corruption detections, Memory behavior changes, common-mode pair false
confidence, common-mode full-loop false accepts, and maximum use of every
bounded resource.

## Frozen falsification criteria

The protected v1 result is **FAILED** if any of these occurs:

- one corrupted channel causes a false committed state;
- stale, wrong-epoch, or wrong-transaction evidence is accepted;
- duplicate A evidence counts as A+B;
- derived B or declared shared-ancestor evidence is accepted as independent;
- Map or Memory commits before a complete authorized pair;
- persistent disagreement is resolved by selecting a source;
- an invalid recovery is authorized;
- corrupt Memory influences Explorer before audit/recovery;
- commit or authorization duplicates;
- any declared bound is exceeded;
- a declared transient disagreement cannot recover; or
- cross-source-authorized Memory no longer changes later Explorer behavior.

The intentional common-mode control is outside the independent-fault-domain
assumption and is reported separately. Its outcome cannot be used to rewrite
the protected criteria or hide a false accept.

## Remaining trust assumptions

The source code and registration binding, fault-domain/lineage declarations,
cross-source authorizer, Measure auditor, coordinator, retained pair store, and
hidden test oracle remain trusted for their respective roles. Physical source
diversity, cryptographic source authentication, hostile collusion, hidden
common causes, concurrency, identifier wrap, and oracle compromise are not
tested.
