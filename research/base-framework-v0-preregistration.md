# Base framework v0 pre-registration

**Status:** frozen before implementation and execution, 2026-09-18.

## Question and scope

Can a four-state, three-action system complete a bounded
Explorer/Map/Measure/Memory/Recovery loop in which protected consequence and
provenance govern continuation, a recovery proposer cannot certify itself, and
audited Memory changes a later Explorer decision?

This is a software research prototype. It is not a general agent, complete
world model, proof of safety, or claim of general recursive self-improvement.
The completed bounded RTL authorization experiment remains an earlier,
unchanged milestone.

## Component contracts

| Component | Inputs and bounded state | Proposal/output | Authoritative evidence | Validation and failure | Authority |
|---|---|---|---|---|---|
| Explorer | Authorized Map state; at most 8 audited Memory records; 3 actions | One action with epoch/transaction/Map provenance | None | Reject unknown, stale, wrong-state, or policy-invalid action | Proposes only; cannot authorize execution or commits |
| Map | One incumbent; action; observation; at most 2 candidates | Transition prediction and state candidate | None | Candidate must match protected environment receipt and provenance | Proposes only; cannot authorize its update |
| Measure | Map prediction and one protected receipt | Match/mismatch verdict | Protected environment receipt | Separate auditor recomputes verdict; wrong identity/lineage/verdict fails | Proposes verdict only |
| Memory | Authorized outcome and protected receipt; 8-record ring | Audited history and record candidate | Paired protected receipt ring | Audit every record before use; quarantine mismatch; rotate oldest pair together | Cannot authorize its own commit |
| Recovery | Verified failure, quarantine, protected evidence; 1 attempt | One correction candidate | None | Separate authorizer requires external lineage, exact content, and provenance | Proposes only; cannot authorize recovery |

All components use only the fields needed by this environment. Mutable
configuration, multiple sources, identifier wrap, and adversarial corruption of
the protected source or authorizer are outside the test.

## Environment and independent ground

The environment has states `{0,1,2,3}` and actions
`{ADVANCE,HOLD,RETREAT}`. A separate module implements an immutable transition
table and emits receipts containing epoch, transaction ID, observation ID,
pre-state, action, next-state, consequence, source identity, and lineage.

Framework code may not import the environment transition helper/table. The Map
uses a separately written conditional model. Environment receipts carry
`EXTERNAL_PROTECTED` lineage and are the ground for transition and recovery
authorization.

## Authority and incumbent policy

Authority states are `PROPOSED`, `OBSERVED`, `MEASURED`, `QUARANTINED`,
`RECOVERING`, `AUTHORIZED`, and `REJECTED`.

- Action execution requires a separate policy/provenance gate.
- Map update requires a candidate/evidence authorizer.
- Memory commit requires audited measurement and authorized state transition.
- Recovery commit requires the same independent evidence route; Recovery cannot
  authorize itself.
- Episode continuation requires all mandatory commits for the transaction.

An incumbent verified valid remains eligible. A newer candidate receives no
preference merely for being new. If no replacement passes and the incumbent is
valid, retain it. If the incumbent is verified invalid, quarantine it; it is not
a fallback. If neither incumbent nor replacement is authorized, stop.

## Minimal provenance and lineage

Transaction provenance is `(epoch, transaction_id, observation_id,
source_identity)`, plus the pre-state/Map version where required.

Lineage classes are:

- `EXTERNAL_PROTECTED` — independently observable environment evidence;
- `CANDIDATE_DERIVED` — derived from the candidate being checked;
- `SHARED_ANCESTOR` — reference and candidate share a declared ancestor.

The protected authorizer accepts only provenance-matched
`EXTERNAL_PROTECTED` evidence. This catches direct categorized circularity. It
does not discover hidden common causes or implement a general causal graph.

## Frozen state limits

| Resource | Maximum |
|---|---:|
| World states | 4 |
| Actions | 3 |
| Map state | 1 incumbent + 2 candidates |
| Memory records | 8 |
| Protected receipts | 8 |
| Quarantine entries per subsystem | 1 |
| Recovery candidates / attempts | 1 / 1 |
| Trace records | 16 |
| Episode transitions | 12 |
| Epochs per scenario | 2 |

Memory and evidence use paired ring rotation. Any other growth beyond these
bounds fails the experiment.

## Predeclared controls and failures

| Scenario | Required outcome |
|---|---|
| Clean episode | Complete 12 transitions; Memory changes a later action |
| Clean incumbent | Valid unchanged state remains authorized |
| Valid replacement | Matching state-changing candidate is authorized |
| Wrong Map state | Detect, quarantine, recover from protected pre-state, continue |
| Corrupted Memory record | Detect before use; prevent corrupt influence; recover from protected receipt |
| Wrong Measure verdict | Separate auditor detects; independently verified correction may commit |
| Invalid Explorer proposal | Reject before environment execution |
| Failed Recovery | Reject candidate; do not continue or retain invalid incumbent |
| Wrong transaction or epoch | Reject on provenance mismatch |
| Shared-descendant reference | Naive checker shows false confidence; real authorizer rejects lineage |
| Stale incumbent | Quarantine; never retain merely because incumbent |
| Recoverable fault | Correct and continue within one attempt |
| Unrecoverable fault | Safely reject with no commit |
| Memory rotation | Stay at 8 records with identities/content intact |
| Epoch transition | Reject stale epoch; accept fresh identities |

## Frozen falsification criteria

The experiment is **FAILED** for its scope if any of these occurs:

- corrupted state reaches authorized history undetected;
- wrong transaction/epoch evidence is accepted;
- invalid recovery is authorized;
- correlated descendant evidence is treated as independent;
- a verified-invalid incumbent is retained as a valid fallback;
- a declared recoverable fault cannot recover;
- a component silently changes environment ground truth;
- bounded state is exceeded;
- commit or authorization duplicates;
- continuation occurs before required authorization; or
- Memory does not change future Explorer behavior.

Safe rejection is not recovery. Detection is not authorization. These criteria
will not be reinterpreted after execution.
