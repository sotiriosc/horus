# Base Framework v2 evidence-provenance results

**Result:** PASS under the frozen protected criteria. Execution date:
2026-09-18. Parent v1 commit:
`4fa4c9bdc3f20d71da2b59bd5ed723bbcc6c90ff`. Implementation commit:
`1166285`.

## 1. Frozen preregistration

The [preregistration](base-framework-v2-preregistration.md) was committed as
`95fde1a` before implementation. It froze the four-state world, three actions,
v1 source semantics, registry, witness, authority rules, bounds, 19 scenario
types, metrics, falsification criteria, and trust-root controls. No protected
criterion was weakened after execution.

## 2. Dependency registry design

The immutable registry contains exactly nine nodes: the permitted world root,
three normal evidence paths, a derived-B path, a shared sensor and its two
children, and a derived-witness path. Each node stores only process ID, parents,
fault domain, evidence type, and allowed authorization role. Candidate data
cannot add or edit nodes.

Declared process-separation walks parent chains and rejects intersecting process
or fault-domain sets after excluding only `TRUE_WORLD`/`WORLD_ROOT`. It detects
registered dependencies; it does not infer missing causal edges.

## 3. Source A/B contracts

The exact v1 Source A table implementation and Source B conditional
implementation were reused unchanged. Each emits an immutable full receipt and
has no commit authority. V2 wraps receipts with process ID, role, and registry
version, then validates those fields against the external registry.

## 4. Witness C contract

C is not a third full source. Its independent flat table emits a four-bit code
`next_state * 3 + (consequence + 1)` plus epoch, transaction, sequence, witness
ID, process ID, and registry version. It imports neither source, Map, framework
checker, nor oracle code. The package checker independently encodes the A/B
claim and compares it with C.

## 5. Hidden oracle design

The unchanged v1 oracle remained test-only. Runtime v2 modules contain no
oracle import. Campaign code used truth only after execution to compare actual
and committed transitions and classify false acceptance.

## 6. Provenance model

Source evidence binds epoch, transaction, observation identity, channel
sequence, source identity, process identity, role, and registry version.
Witness evidence binds the same transaction coordinates to a witness identity
and process path. An authorized package records the two observation IDs,
witness ID, process triple, and registry version. Memory keeps its minimal v1
record plus the separate bounded package decision; it does not copy the graph.

## 7. Authority model

Evidence production only stages data. The package authorizer requires valid
A/B/C provenance, A/B agreement, C relation agreement, valid registered roles
and types, and pairwise declared separation. Only then does the package enter
the unchanged v1 Measure, state, recovery, Memory, and continuation gates.
Failure quarantines the transaction for one re-observation and then stops.
Recovery remains a proposer and cannot create C, edit the registry, or
authorize itself.

## 8. Implementation tree

| File | Purpose |
|---|---|
| `registry.py` | immutable registry and path validation |
| `types.py` | immutable evidence/package records |
| `witness_c.py` | independent four-bit witness |
| `framework.py` | package gate and v1 adapter |
| `campaign.py` | scenarios and external recomputation |
| `test_framework.py` | 13 boundary and campaign tests |
| `run.py` | external evidence writer |
| `results.json` | compact measured summary |

## 9. Bounded-state limits

Observed maxima matched the frozen limits: 9 registry nodes, 3 staged evidence
items, 1 pending transaction, 2 observation rounds, 1 re-observation, 8 Memory
records, 8 pair decisions, 8 package decisions, and 24 records in each runtime
trace. The world stayed at four states, three actions, and 12 transitions per
clean episode. No bound was exceeded.

## 10. Positive-control results

All three clean episodes completed 12 authorizations. A, B, and witness
transients recovered in 9/9 runs after one clean re-observation. Valid state
recovery, corrupted-Memory recovery, wrong-Measure correction, and epoch
transition controls committed correctly in 12/12 runs combined.

## 11. A+B common-mode results

The central control presented identical wrong A+B transitions while correct C
disagreed. All six rounds across three seeds were blocked. When C was corrupted
to a different relation, all six rounds were also blocked. Thus the two
protected scenarios produced 12/12 package blocks and zero authorization.

## 12. A+B+C common-mode result

**OUT-OF-MODEL TRUST-ROOT FALSE ACCEPT: 3/3.** When all three registered paths
carried the same wrong relation, package checks passed and the inherited
recovery path committed it. Only the hidden oracle exposed the error. This
result is separate from the protected count and limits the v2 claim.

## 13. False-process-independence control

A B receipt explicitly registered as a descendant of A was rejected on both
rounds in all three seeds. A/B evidence under a shared registered sensor was
also rejected on both rounds in all seeds. Numerical agreement never
compensated for failed process separation: 12 process-separation rejections.

## 14. Candidate-derived witness control

A correct-looking C registered under `DERIVED_WITNESS`, a child of A, was
rejected on both rounds in all seeds: six candidate-derived rejections and zero
commits.

## 15. Registry-corruption negative control

**OUT-OF-MODEL TRUST-ROOT FALSE ACCEPT: 3/3.** A deliberately false registry
declared derived B and C paths to be separate. Runtime validation then accepted
the wrong evidence package, while the oracle found every false commit. Registry
integrity is therefore a real root of trust, not administrative metadata.

## 16. False accepts

Protected false accepts: **0**. Out-of-model false accepts: **6**, split evenly
between identical A+B+C corruption and registry corruption. The two counts are
never combined to soften or reinterpret the protected result.

## 17. False rejects

Externally observed false rejects: **0**. Every predeclared valid clean,
transient, recovery, Measure, Memory, and epoch control completed as expected.

## 18. Duplicate authorizations

Duplicate authorizations: **0**. A witness offered in the B role caused six
duplicate-witness rejections and no commit. Package, pair, and Memory rings
rotated together under their eight-entry bounds.

## 19. Recovery results

Nine source/witness transients recovered after re-observation. Three corrupted
Memory records were detected before Explorer use and rebuilt from retained
authorized decisions. Three wrong Measure verdicts were corrected. Three
invalid state-recovery proposals were rejected. Recovery never supplied its own
witness or registry fact.

## 20. Memory → Explorer behavior evidence

In each clean seed, state 1 first selected `ADVANCE`. The authorized negative
consequence changed the later state-1 choice to `HOLD`. This occurred in 3/3
episodes while Memory, pair, and package rings each retained eight aligned
entries.

## 21. External audit results

After every scenario, campaign code independently recomputed registry ancestry,
compared actual and committed transitions with the hidden oracle, identified the
package and paths used, and classified false acceptance. It did not call the
runtime separation method. The audit confirmed zero protected false accepts and
found all six trust-root false accepts.

## 22. Falsification table

| Frozen protected criterion | Result |
|---|---|
| Wrong A+B accepted while correct C disagrees | PASS: 0; 6/6 rounds blocked |
| Candidate-derived C counted as separate | PASS: 6 rejections |
| Registered shared ancestry counted as separate | PASS: 6/6 rounds rejected |
| Stale witness provenance accepted | PASS: 6 rejections |
| Spoofed process accepted | PASS: 6 process-identity rejections |
| Commit before complete A+B+C package | PASS: none |
| Invalid recovery authorized | PASS: 3 rejected |
| Corrupt Memory affects Explorer before audit | PASS: 3 detected/rebuilt |
| Duplicate authorization | PASS: 0 |
| Declared bound exceeded | PASS: none |
| Declared transient cannot recover | PASS: 9/9 recovered |
| Memory behavior change lost | PASS: observed 3/3 |

## 23. Updated hardware mapping

The [mapping](../docs/HARDWARE_FRAMEWORK_MAPPING.md) now covers a tiny process
registry, source-pair validator, witness interface and checker, package
assembler, quarantine, retry controller, and composite gate. All v2 RTL is
PROPOSED. No v2 RTL, synthesis, timing, power, area optimization, or physical
separation result was produced.

## 24. Remaining trust roots

The true-world interface, witness implementation, registry completeness and
integrity, package authorizer, inherited authorizers, coordinator, and test
oracle remain trusted. Undeclared common causes, physical coupling, collusion,
hostile code replacement, identifier wrap, concurrency, and false dependency
facts remain outside the protected model.

The framework progression is precise: v0 used one trusted protected evidence
channel; v1 used two declared-independent full observation channels with
disagreement handling; v2 uses multiple evidence relations, explicit declared
process-dependency validation, and a smaller orthogonal witness.

## 25. Narrowest defensible conclusion

**SUPPORTED UNDER TESTED CONDITIONS:** a bounded five-component framework can
require provenance-matched evidence from declared distinct production paths
plus an independently generated orthogonal witness, and can block the tested
identical A+B common-mode corruption when the witness path remains correct.

This is not proof of causal independence, truth verification, common-mode
immunity, Byzantine fault tolerance, general grounding, or general safety.

## 26. Recommended next experiment

V3 should keep the world and policy fixed and test integrity of the dependency
registry and witness-production root. Pre-register an external or renewed
challenge that can reveal one false registry edge or a shared A/B/C cause,
while preserving package provenance and checker independence. Do not add a
fourth vote. The two observed 3/3 trust-root failures should be the required
negative controls.

## Reproduction

```bash
make test
make independent-commit
make independent-commit-followup
make base-framework-v0
make base-framework-v1
make base-framework-v2
```
