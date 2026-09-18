# Public research checkpoints

Chronology: Horus baseline → bounded independent authorization → five-component
v0 → cross-source v1 → evidence-process provenance v2. Each SHA identifies the
original milestone, including its original results. Later documentation does
not rewrite those checkpoints. All results are limited to tested conditions;
identity seeds are repetitions, not independent statistical samples.

## Horus baseline

- **Commit:** `8f7bee46ffe74d225de71d1ceeec6f29d3c41f60`
- **Research question:** Can reduced-precision arithmetic, normalization, scale
  tracking, routing, and local detection/replay be made reproducible?
- **What passed:** The documented public core RTL/reference checks; the current
  preserved core entry point executes 53 steps.
- **Key negative control:** Precision-losing block-FP and feedback-chain
  outcomes remain recorded as limitations, not successful repairs.
- **Remaining trust boundary:** Reference specifications and local control;
  repair completion alone does not independently authorize continuation.
- **Narrowest defensible result:** Reproducible bounded hardware primitives,
  with workload-specific numerical and fault-detection limits.

## Bounded independent authorization

- **Commit:** `fb0c7122b3c8e79e2f89e1b50453fafda055eec2`
- **Research question:** Can a separate checker authorize repaired candidates
  from protected pre-fault evidence?
- **What passed:** 4,200 protected transactions; zero false accepts, false
  rejects, or duplicates. The follow-up passed 2,700 broader-fault transactions
  and 21 paired trace comparisons.
- **Key negative control:** A descendant-reference checker falsely accepted
  300 corrupted proposals.
- **Remaining trust boundary:** Protected source, checker, identity allocator,
  and gate control; unsupported patterns are rejected, not repaired.
- **Narrowest defensible result:** Protected-source identity/content checks
  separate repair proposals from downstream authorization in the tested model.

## Base Framework v0

- **Commit:** `6752f0adf591bf6ceacfe4b07cee967075f49c20`
- **Research question:** Can Explorer, Map, Measure, Memory, and Recovery form a
  bounded loop in which authorized consequence changes later action?
- **What passed:** 12 tests / 42 scenarios; zero protected false accepts, false
  rejects, or duplicates; 21 authorized recoveries and 9 invalid recoveries
  rejected; `ADVANCE → HOLD` in all three clean episodes.
- **Key negative control:** A correlated checker agreed with three wrong
  descendant references; the protected gate rejected all three.
- **Remaining trust boundary:** One trusted evidence channel, declared lineage,
  environment, authorizers, and coordinator.
- **Narrowest defensible result:** The five-component loop works in the fixed
  four-state world, with independent authorization of recovery proposals.

## Base Framework v1 — cross-source grounding

- **Commit:** `4fa4c9bdc3f20d71da2b59bd5ed723bbcc6c90ff`
- **Research question:** Can two separately implemented observation channels
  gate the same loop and handle declared single-channel faults?
- **What passed:** 10 tests / 69 scenarios; zero protected false accepts, false
  rejects, or duplicates; 12 transient/stale recoveries; persistent evidence
  disagreement stopped after one re-observation; Memory behavior retained.
- **Key negative control:** Identical A+B common-mode corruption caused 3/3
  out-of-model false accepts, detected by the hidden test oracle.
- **Remaining trust boundary:** Actual channel diversity, declared domains and
  port registration, authorizers, coordinator, and oracle correctness.
- **Narrowest defensible result:** Provenance-matched pairs handle the tested
  single-channel faults; agreement does not establish truth.

## Base Framework v2 — evidence-process provenance

- **Commit:** `bdac607af38bf7a693e1d98db64cc8d2df9a48fa`
- **Research question:** Can a tiny declared dependency registry and a smaller,
  independently generated witness C challenge agreeing A+B evidence?
- **What passed:** 13 tests / 57 scenarios; zero protected false accepts, false
  rejects, or duplicate authorizations; 9/9 transient source/witness faults
  recovered; Memory behavior retained.
- **Common-corruption blocks:** 12/12 tested A+B package rounds were blocked:
  **6/6 with correct C**, plus **6/6 with C corrupted differently**. The original
  evidence does not support describing all 12 rounds as having correct C.
- **Key negative controls:** Identical A+B+C corruption caused 3/3 out-of-model
  trust-root false accepts; a corrupted trusted registry also caused 3/3.
- **Remaining trust boundary:** True-world interface, witness implementation,
  registry completeness/integrity, authorizers, coordinator, and hidden oracle;
  undeclared common causes remain unsolved.
- **Narrowest defensible result:** Under the tested assumptions, complete
  provenance-matched evidence packages with declared process separation and an
  independent witness block the tested identical A+B corruption when C remains
  correct. This is not proof of causal independence or common-mode immunity.

## Reproduction and original evidence

Run `make test`, `make independent-commit`, `make independent-commit-followup`,
`make base-framework-v0`, `make base-framework-v1`, and `make base-framework-v2`.
See [reproducibility](../docs/REPRODUCIBILITY.md),
[authorization results](bounded-independent-authorization-results.md),
[v0 results](base-framework-v0-results.md), [v1 results](base-framework-v1-results.md),
[v2 results](base-framework-v2-results.md), and the
[hardware mapping](../docs/HARDWARE_FRAMEWORK_MAPPING.md).
