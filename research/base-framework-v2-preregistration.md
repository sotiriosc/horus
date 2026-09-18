# Base framework v2 evidence-provenance pre-registration

**Status:** frozen before implementation and execution, 2026-09-18.

**Parent milestone:** Base Framework v1 commit
`4fa4c9bdc3f20d71da2b59bd5ed723bbcc6c90ff`. V0, v1, the public baseline,
and bounded independent-authorization results remain immutable.

## Research question

Can the unchanged bounded Explorer/Map/Measure/Memory/Recovery loop block the
tested identical A+B corruption by requiring a complete evidence package whose
production paths pass a declared process-separation rule and whose transition
also matches a smaller, independently generated witness C?

V2 validates an explicit dependency registry. It does not infer causal
structure, prove physical independence, or eliminate roots of trust.

## Frozen world and inherited loop

The experiment retains exactly the v0/v1 four states, three actions, 12
transition/consequence cases, deterministic Memory-scored Explorer, Map,
predictive Measure, eight-record Memory, one-attempt Recovery, Source A table
semantics, Source B conditional semantics, and one re-observation policy. No
policy, environment, or source-count expansion is allowed.

## Immutable evidence-process registry

The normal registry is an immutable tuple/mapping created outside transaction
and candidate state. Each node contains only `process_id`, parent process IDs,
`fault_domain`, `evidence_type`, and `allowed_authorization_role`. Registry
version is bound into each evidence wrapper and package decision.

| Process | Parent(s) | Domain | Evidence type | Allowed role |
|---|---|---|---|---|
| `TRUE_WORLD` | none | `WORLD_ROOT` | root | none |
| `OBSERVATION_PATH_A` | `TRUE_WORLD` | `OBSERVATION_A` | full receipt | source A |
| `OBSERVATION_PATH_B` | `TRUE_WORLD` | `OBSERVATION_B` | full receipt | source B |
| `WITNESS_PATH_C` | `TRUE_WORLD` | `WITNESS_C` | relation code | witness |
| `DERIVED_B_REFERENCE` | `OBSERVATION_PATH_A` | `OBSERVATION_A` | full receipt | source B |
| `SHARED_SENSOR` | `TRUE_WORLD` | `SHARED_SENSOR` | dependency | none |
| `SHARED_PATH_A` | `SHARED_SENSOR` | `SHARED_SENSOR` | full receipt | source A |
| `SHARED_PATH_B` | `SHARED_SENSOR` | `SHARED_SENSOR` | full receipt | source B |
| `DERIVED_WITNESS` | `OBSERVATION_PATH_A` | `OBSERVATION_A` | relation code | witness |

Normal registry node bound: 9. Candidate data cannot add or edit nodes. The
campaign may deliberately instantiate a corrupted registry in one separately
classified out-of-model control.

## Declared process-separation validation

For A, B, and C, the authorizer walks the registered parent chains. Two paths
are declared separated only if their ancestor/process and fault-domain sets do
not intersect, excluding the explicitly permitted `TRUE_WORLD`/`WORLD_ROOT`.
Every process must exist, have the correct evidence type/role, and bind to the
registry version.

This catches registered derivation and shared dependencies. It cannot discover
an absent/false registry edge, physical coupling, collusion, or an undeclared
common cause. The result will be called **declared process-separation
validation**, never proof of causal independence.

## Source A/B contracts

V1 Source A and B implementations remain unchanged. Each receives epoch,
transaction, true transition pre-state, action, and observation sequence. A
uses its explicit table and B its conditional implementation. Each emits its
minimal immutable v1 receipt and has no authorization power.

V2 wraps each receipt with `(process_id, evidence_role, registry_version)`.
These fields are checked against the external registry; labels alone do not
establish a valid process path.

## Witness C contract

Witness C is a third independently implemented, low-bandwidth relation to the
same transition, not a full Source A/B copy.

- **Input:** epoch, transaction, actual pre-state, action, observation sequence.
- **Implementation:** an independent flat transition-code table; imports no A,
  B, Map, framework checker, or hidden-oracle code.
- **Output:** immutable `(epoch, transaction_id, witness_id,
  channel_sequence, process_id, registry_version, relation_code)`.
- **Relation code:** a 4-bit value encoding the observed next-state and ternary
  consequence class for the fixed world. It omits pre-state, action, full
  source receipt, lineage, and candidate state.
- **Authority:** proposes witness evidence only; cannot authorize, repair,
  choose a source, or edit the registry.

The package checker independently encodes the A/B claimed next-state and
consequence and requires exact witness-code agreement plus provenance.

## Hidden oracle

The unchanged v1 oracle is imported only by campaign/tests. Runtime v2, registry,
witness, sources, Map, Measure, Memory, Recovery, and authorizers cannot access
it. After every transaction, campaign code compares commit/Memory/Map with
oracle truth and separately recomputes package structure and registered paths.

## Evidence package and provenance

One package contains registered A evidence, registered B evidence, one witness
C, and registry version. Its decision identity binds epoch, transaction,
observation sequence, A/B observation IDs, witness ID, and process IDs.

Authorization requires valid A/B/C provenance; A/B transition agreement;
witness relation agreement; valid roles/types/version; pairwise declared
process separation except the permitted world root; no derived/disallowed
path; and all inherited v0/v1 Measure, state, recovery, Memory, and continuation
gates. Agreement cannot compensate for failed separation, and separation cannot
compensate for content mismatch.

## Authority and disagreement policy

Used states are `PROPOSED`, `OBSERVED_PARTIAL`, `OBSERVED_PAIRED`, `WITNESSED`,
`PROCESS_VALIDATED`, `MEASURED`, `QUARANTINED`, `REOBSERVING`, `RECOVERING`,
`AUTHORIZED`, and `REJECTED`.

- Registered ports produce data only.
- EvidencePackageAuthorizer alone validates A+B+C and registry paths.
- First/second evidence items remain staged; no Map/Memory commit occurs.
- Invalid/incomplete package quarantines one transaction and permits exactly one
  new observation round.
- Persistent failure stops; no source or witness is selected as truth.
- An authorized package may feed the unchanged v1 Measure/state/Memory gates.
- Recovery proposes only after package authorization and cannot generate C,
  edit the registry, relabel evidence, or authorize itself.
- Continuation requires package, Measure, state, and Memory authorization.

Memory stores the existing minimal transition identity plus package decision
identity. The immutable registry remains separate. An eight-entry authorized
package ring rotates atomically with the eight Memory records/pair decisions.

## Frozen bounds

| Resource | Maximum |
|---|---:|
| World states / actions | 4 / 3 |
| Main sources / witnesses | 2 / 1 |
| Registry nodes | 9 fixed |
| Evidence items per round | 3 |
| Observation rounds / re-observations | 2 / 1 |
| Pending/quarantined transactions | 1 |
| Map | 1 incumbent + 2 candidates |
| Memory / pair decisions / package decisions | 8 / 8 / 8 |
| Recovery candidates / attempts | 1 / 1 |
| Candidate replacements per transaction | 1 |
| Episode transitions / epochs per scenario | 12 / 2 |
| Runtime package trace / inherited runtime trace | 24 / 24 |
| Driver audit trace | 24 |
| Authorization identities per epoch | 24 |

Any unplanned growth or unpaired eviction fails the protected experiment.

## Frozen scenarios and expected outcomes

Each scenario runs for epoch seeds 1, 2, and 3. Seeds vary identity only.

| Scenario | Expected result |
|---|---|
| Clean episode | 12 complete-package commits; Memory changes state-1 `ADVANCE → HOLD` |
| A transient fault | A disagrees; one clean re-observation; authorize |
| B transient fault | Symmetric recovery |
| Witness transient fault | A/B correct, C wrong; one clean re-observation; authorize |
| Valid state recovery | Stale Map quarantined; package-grounded recovery authorized |
| Corrupted Memory | Detect before Explorer; rebuild only with retained authorized package |
| Invalid recovery | Wrong candidate rejected |
| A+B identical common corruption, C correct | Package blocked both rounds; safe reject |
| A+B identical common corruption, C corrupted differently | No package; safe reject |
| A+B+C identical common corruption | Out-of-model; package may false-accept; oracle scores |
| False process separation | B copied from A under `DERIVED_B_REFERENCE`; registry rejects |
| Shared registered ancestor | A/B agree under shared registered parent; registry rejects |
| Candidate-derived witness | Correct-looking C under `DERIVED_WITNESS`; registry rejects |
| Stale witness | Correct content with wrong epoch/transaction; reject after bounded retry |
| Duplicate witness | One C cannot occupy another evidence role; reject |
| Spoofed process ID | Unknown/role-inconsistent process rejected |
| Wrong Measure verdict | Independent Measure auditor corrects; authorize |
| Epoch transition | Fresh package authorizes; stale evidence cannot |
| Corrupted registry | Out-of-model registry hides derivations; false confidence may commit; oracle scores |

## Out-of-model controls

1. **A+B+C identical common corruption:** all three normal registered paths
   agree on one wrong relation. Any wrong commit is
   `OUT_OF_MODEL_TRUST_ROOT_FALSE_ACCEPT` and is not folded into the protected
   false-accept count.
2. **Corrupted registry:** the harness supplies a false trusted registry that
   relabels derived B and derived C paths as separated. Any wrong commit is also
   `OUT_OF_MODEL_TRUST_ROOT_FALSE_ACCEPT`.

These outcomes will be recorded, not repaired after observation. They define
the remaining trust roots.

## Frozen metrics and result classes

Result classes: `TRUE_ACCEPT`, `SAFE_REJECTION`, `SUCCESSFUL_RECOVERY`,
`FALSE_ACCEPT`, `FALSE_REJECT`, and `OUT_OF_MODEL_TRUST_ROOT_FALSE_ACCEPT`.

Metrics include clean authorizations, protected false accepts, external false
rejects, duplicate authorizations, A/B disagreements, witness disagreements,
re-observations, successful transient recoveries, persistent rejections,
process-separation/candidate-derived/stale/spoof rejections, invalid recovery,
Memory corruption and behavior changes, A+B common attempts/blocks, A+B+C false
accepts, registry-corruption false accepts, and maximum bounded-state use.

## Frozen falsification criteria

The protected v2 claim is **FAILED** if:

- identical wrong A+B is authorized while correct C disagrees;
- candidate-derived C counts as independent;
- registered shared ancestry counts as separated;
- stale/wrong witness provenance is accepted;
- an unknown/role-inconsistent process identity is accepted where modeled;
- any Map/Memory commit occurs before complete package authorization;
- invalid recovery is authorized;
- corrupted Memory affects Explorer before audit/recovery;
- authorization/commit duplicates;
- any declared bound is exceeded;
- a declared transient A, B, or C fault cannot recover; or
- authorized Memory no longer changes later behavior.

The two out-of-model trust-root controls are reported separately and cannot be
used to weaken or reinterpret protected criteria.

## Explicit remaining trust assumptions

The true-world interface supplied to evidence processes, witness implementation,
normal registry completeness/integrity, package authorizer, inherited
Measure/state/Memory gates, coordinator, and hidden oracle for scoring remain
trusted. Undeclared common causes, false registry facts, physical coupling,
collusion, hostile code replacement, concurrency, identifier wrap, and oracle
compromise are not solved.
