# Base framework v0: public results

**Status:** IMPLEMENTED and OBSERVED on 2026-09-18. The predeclared bounded
experiment passed. The result is SUPPORTED UNDER TESTED CONDITIONS only.

The frozen contracts and falsification rules are in the
[pre-registration](base-framework-v0-preregistration.md). The executable source
and compact result are in [`experiments/base_framework_v0/`](../experiments/base_framework_v0/).

## 1. Component contracts

| Component | Proposal/state | Ground or checker | May authorize | May not authorize |
|---|---|---|---|---|
| Explorer | One of three actions, based on current Map and at most eight audited outcomes | Current protected pre-state plus action/provenance gate | Nothing | Execution, Map/Memory commit, continuation |
| Map | Prediction and one state candidate; one incumbent | Environment consequence receipt and StateAuthorizer | Nothing | Its own update or candidate selection |
| Measure | Match/mismatch verdict for predicted versus realized consequence | EvidenceAuditor independently recomputes from protected receipt | Nothing | Its verdict, recovery, or continuation |
| Memory | Eight authorized outcome records in paired rotation with eight receipts | RecordAuthorizer and protected receipt ring | Nothing | Its own record or a policy decision |
| Recovery | One correction candidate in one attempt | StateAuthorizer, RecordAuthorizer, or EvidenceAuditor | Nothing | Declaring its proposed correction successful |

The full input, output, state, evidence, failure, provenance, and resource
contracts were frozen before code was written.

## 2. Environment definition

The independent environment implements this complete finite table. Each cell is
`(next_state, consequence)`.

| State | ADVANCE | HOLD | RETREAT |
|---:|---:|---:|---:|
| 0 | `(1,+1)` | `(0,0)` | `(3,-1)` |
| 1 | `(2,-1)` | `(1,+1)` | `(0,0)` |
| 2 | `(3,+1)` | `(2,0)` | `(1,+1)` |
| 3 | `(0,-1)` | `(3,0)` | `(2,+1)` |

`environment.py` imports no framework code. `framework.py` imports no
environment implementation. A complete 12-case cross-check showed that the two
independently written transition implementations agree.

## 3. Authority model

| Decision | Proposer | Authority | Commit/continuation rule |
|---|---|---|---|
| Action execution | Explorer | ActionAuthority | Exact current epoch, transaction, pre-state, Map version, allowed action, and protected snapshot required |
| Map update | Map or Recovery | StateAuthorizer | Candidate must match external receipt content, identity, source, and accepted lineage |
| Measure correction | Recovery | EvidenceAuditor | Auditor recomputes the verdict independently from the protected receipt |
| Memory commit/recovery | Coordinator or Recovery | RecordAuthorizer | Every field must match its paired protected receipt |
| Episode continuation | Coordinator | Composite result of all required gates | Staged Map and Memory commits apply only after both are authorized |

Authority states are explicit: `PROPOSED`, `OBSERVED`, `MEASURED`,
`QUARANTINED`, `RECOVERING`, `AUTHORIZED`, and `REJECTED`. Safe rejection
withdraws continuation authority for that episode.

## 4. Provenance model

State and consequence evidence carries `(epoch, transaction_id,
observation_id, source_identity)`. Action proposals also bind the pre-state and
Map version. The three declared lineage classes are `EXTERNAL_PROTECTED`,
`CANDIDATE_DERIVED`, and `SHARED_ANCESTOR`. Only a provenance-matched protected
receipt can ground authorization.

This model identifies declared direct circularity and mismatched identities. It
does not discover hidden common causes, authenticate hostile sources, or form a
general causal graph.

## 5. Bounded-state limits

| Resource | Frozen maximum | Observed |
|---|---:|---:|
| World states / actions | 4 / 3 | 4 / 3 |
| Map | 1 incumbent + 2 candidates | Within bound |
| Memory / protected receipts | 8 / 8 | 8 / 8 |
| Quarantine entries per subsystem | 1 | 1 |
| Recovery candidates / attempts | 1 / 1 | 1 / 1 |
| Trace records | 16 | At most 16 |
| Episode transitions | 12 | 12 |
| Epochs per scenario | 2 | At most 2 |
| Authorization identity records per epoch | 24 | At most 12 |

The clean run forced four paired Memory/evidence evictions per seed. Identity
and content remained valid after rotation. The 24-entry authorization-ledger
limit is derived from at most two observation positions for each of 12 bounded
transactions. One recovery attempt means zero retries.

## 6. Implementation tree

```text
experiments/base_framework_v0/
├── environment.py       independent four-state ground and protected receipts
├── framework.py         five components, authority gates, bounded coordinator
├── campaign.py          frozen clean and fault-injection scenarios
├── test_framework.py    independent boundary and full-loop checks
├── run.py               fail-closed public runner
├── results.json         compact approved evidence
└── README.md            reproduction and scope
```

`make base-framework-v0` is the public entry point. Run evidence is created in
a new directory outside the repository.

## 7. Clean control results

Three clean episodes completed 12 transitions each. All 36 transactions
committed and continued. Each run reached the eight-record bound, evicted four
oldest Memory/receipt pairs, and retained exact pairing. Across the complete
campaign, 87 transactions committed from 96 world executions.

The three seeds vary epoch identities; the environment and policy remain
deterministic. They are identity repetitions, not statistical sampling.

## 8. Failure-injection results

Every named scenario passed in all three seed/epoch runs.

| Injection/control | Required and observed result |
|---|---|
| Wrong Map state | Incumbent quarantined; protected pre-state recovery authorized; continued |
| Corrupted Memory consequence | Detected before Explorer use; rebuilt from paired protected receipt |
| Wrong Measure verdict | Separate auditor detected it; independently recomputed correction committed |
| Invalid Explorer action | Rejected before environment execution |
| Failed state recovery | Invalid candidate rejected; no commit or continuation |
| Wrong transaction | Mismatched candidate rejected; fresh recovery separately authorized |
| Wrong epoch / epoch transition | Stale candidate rejected; fresh-epoch recovery authorized |
| Shared-descendant reference | Correlated checker agreed incorrectly; real authority rejected lineage |
| Stale incumbent | Verified-invalid incumbent quarantined, never used as fallback |
| Bad candidate with valid incumbent | Valid unchanged incumbent retained |
| Unrecoverable fault | Safely rejected with no history commit or continuation |
| Invalid Memory recovery | Rebuilt record rejected; Explorer did not continue |

## 9–11. Acceptance and authorization counts

| Metric | Observed |
|---|---:|
| Protected false accepts | 0 |
| False rejects of valid protected transitions | 0 |
| Duplicate authorizations | 0 |

The protected false-accept figure was recomputed from committed records and the
separate receipt ring after each scenario. It is not only an internal counter.
Zero observed errors is limited to these 42 runs and trust assumptions.

## 12. Recovery results

There were 21 authorized recoveries and 9 rejected recoveries. Authorized
recoveries covered stale Map pre-state, corrupted Memory, wrong Measure verdict,
candidate provenance mismatch, and fresh-epoch replacement. Rejected recoveries
were deliberately wrong state candidates or Memory records. Each recovery used
one candidate and one attempt. The proposing Recovery object had no authority
to accept its output.

## 13. Incumbent/candidate results

The campaign recorded 27 valid incumbent retentions, 51 candidate replacements,
and 21 incumbent quarantines. A valid incumbent beat a bad newer candidate in
all three controls. A verified-invalid incumbent was quarantined in every stale
or failed-recovery control and was never treated as a valid fallback. These are
bounded selection results, not monotonic-improvement evidence.

## 14. Shared-descendant negative control

The deliberately invalid value-agreement checker reported confidence in all
three corrupted shared-ancestor controls. The real authorizer rejected all
three because `SHARED_ANCESTOR` is not independent protected evidence. The
negative control cannot reach a commit path.

## 15. Memory changed future behavior

At state 1, the initial tie-breaking policy selected `ADVANCE`. The protected
consequence for that transition was `-1`. On the next visit to state 1, audited
Memory gave `HOLD` a higher score, so Explorer selected `HOLD`; later visits
kept that choice. The change occurred in all three clean episodes. Removing the
outcome records would restore the initial `ADVANCE` tie break.

## 16. Falsification criteria

| Frozen criterion | Result | Evidence |
|---|---|---|
| Corrupt state reaches authorized history | PASS | 0 protected false accepts; post-commit receipt rechecks |
| Wrong transaction/epoch accepted | PASS | 12 provenance rejections; mismatched candidates never authorized |
| Invalid recovery authorized | PASS | 9 invalid recoveries rejected |
| Descendant evidence treated as independent | PASS | 3 correlated agreements, 3 lineage rejections, 0 commits |
| Verified-invalid incumbent retained | PASS | 21 quarantines; failed cases stopped |
| Declared recoverable fault cannot recover | PASS | 21 declared recoveries authorized |
| Component changes environment ground | PASS | separate environment; framework has no oracle import or write route |
| State exceeds declared bound | PASS | bounds asserted throughout all runs |
| Commit/authorization duplicates | PASS | 0 duplicates; unique authorized identities checked |
| Continuation before mandatory authorization | PASS | staged Map/Memory commit and composite continuation gate |
| Memory fails to change later behavior | PASS | `ADVANCE → HOLD` observed at state 1 in 3/3 clean runs |

No criterion failed in the executed scope.

## 17. Updated hardware mapping

The current mapping is in
[`docs/HARDWARE_FRAMEWORK_MAPPING.md`](../docs/HARDWARE_FRAMEWORK_MAPPING.md).
The complete loop remains software. Existing Horus bounded-commit RTL is a
candidate primitive at the state/recovery boundary, but this experiment did not
claim that every Python component already exists in hardware. No new synthesis
or area optimization was performed.

## 18. Limitations

- The environment, protected receipt path, authorizers, coordinator, and source
  identity labels are trusted. Common-mode faults across them were not tested.
- Lineage is declared metadata, not discovered causality or cryptographic proof.
- The Map/environment pair is independently written but implements the same
  small deterministic function; design misunderstanding could affect both.
- Rejection after environment execution does not roll the environment back. It
  prevents framework commit and continuation.
- Seeds vary identities, not policy or stochastic transitions.
- Identifier wrap, multiple sources, hostile replay, concurrency, power loss,
  timing, RTL realization, synthesis cost, and physical faults were not tested.
- The result does not establish a general agent, general world model, grounding,
  recursive self-improvement, safety, or universal fault tolerance.

## 19. Narrowest defensible conclusion

SUPPORTED UNDER TESTED CONDITIONS: this implementation completes a bounded
five-component software loop in which verified consequence changes a later
action, wrong state/evidence/recovery can remove continuation authority, and a
recovery proposer cannot authorize its own candidate. The conclusion applies
only to the declared four-state environment, fixed contracts, explicit lineage
labels, and trusted protected-source/authority boundary.

## 20. Recommended next experiment

PROPOSED: keep the world and policy fixed, then add a second independently
implemented observation channel and inject faults into the currently trusted
protected receipt, source label, and authorizer inputs. Predeclare which
cross-source disagreements must stop and which can recover. This tests the
largest remaining trust assumption without enlarging the agent, optimizing
hardware, or confusing more scenarios with stronger independence.

## Reproduction

```bash
make test
make independent-commit
make independent-commit-followup
make base-framework-v0
```

Observed verification for this branch: 53 existing core steps passed; the
unchanged earlier campaigns passed 4,200 protected and 2,700 broader-fault
transactions; 12 framework unit tests and 42 framework scenario runs passed.
