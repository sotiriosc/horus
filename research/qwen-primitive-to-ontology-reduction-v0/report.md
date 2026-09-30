# Qwen Primitive-to-Ontology Reduction v0 — completed report

Registered result: **PRIMITIVE_TO_ONTOLOGY_REDUCTION_NOT_ESTABLISHED**. Interpretation: **EXPLICIT_PRIMITIVE_REDUCTION_NOT_ESTABLISHED**.

Exact accuracy **43/50**; schema-valid **50/50**. Scheduled / attempted / completed: **50 / 50 / 50**. Secondary pair gate: **FAIL**.

The overall 43/50 threshold is met, but the historical class scores 5/10 against the mandatory 8/10 floor. Five of seven errors are historical states (four selected no diagnosis; one selected insufficient evidence). The other errors are D→U and N→T. This is a mixed result: strong sufficiency and contradiction performance with unresolved historical/current composition. The changing-pair floor also fails (11/15 against 12/15); the stable-pair floor passes (8/10).

## Frozen provenance

- Branch: `research/qwen-primitive-to-ontology-reduction-v0`
- Verified base: `67053bb802a7851e91b4e7aeb675a687875b8115`
- Method Freeze: `e3f07c01b0d4600559dc3b48591586501b329486`
- Case Freeze: `95ae19a2b2200a68a7db7f9934bb2fe5ac697422`
- Raw pre-scoring commit: `b1b0aad0da0438e1d10c29d6e4fb31cdbf920615`
- Final publication SHA: the verified remote branch head reported in the completion handoff (a document cannot embed its own commit SHA).
- Seed: `739182647`
- Model SHA256: `500a8806e85ee9c83f3ae08420295592451379b4f8cf2d0f41c15dffeb6b81f0`
- llama.cpp: b11242 / `526c43b8f7dfea9032e9f35e7a1be9183ca7cc20`
- Executable SHA256: `778f1b3fbbb76e921af1d7f25a5b61d82859962dcd18c71ce86ab84d7f4884e5`

Same Qwen3-14B Q4_K_M runtime: context 16384; one slot; f16 KV; reasoning on / DeepSeek / budget 512; temperature .2, top_p .9, top_k 40, min_p .05, max_tokens 2048; cache disabled. 41/41 layers offloaded; inherited CPU-mapped embedding buffer retained. Native reasoning is private and non-authoritative.

## Classes and confusion

| Gold class | Correct | Total |
|---|---:|---:|
| SUPPORTED_CURRENT_DEFECT | 9 | 10 |
| NO_SUPPORTED_DIAGNOSIS | 9 | 10 |
| INSUFFICIENT_EVIDENCE | 10 | 10 |
| HISTORICAL_DEFECT_NOT_CURRENT | 5 | 10 |
| INVALID_OR_CONTRADICTORY_EVIDENCE | 10 | 10 |

Matrix: rows gold, columns selected. D = current defect; N = no diagnosis; U = insufficient; T = historical; X = contradictory.

| Gold / selected | D | N | U | T | X | Invalid output |
|---|---:|---:|---:|---:|---:|---:|
| D | 9 | 0 | 1 | 0 | 0 | 0 |
| N | 0 | 9 | 0 | 1 | 0 | 0 |
| U | 0 | 0 | 10 | 0 | 0 | 0 |
| T | 0 | 4 | 1 | 5 | 0 | 0 |
| X | 0 | 0 | 0 | 0 | 10 | 0 |

## Pairs, strata and diagnostics

Changing pairs: **11/15** (gate 12). Stable pairs: **8/10** (gate 8). Every pair differs in exactly one supplied primitive field.

| Stratum | Correct | Total |
|---|---:|---:|
| IRRELEVANT_CHANGE | 18 | 20 |
| PRECEDENCE | 23 | 28 |
| SIMPLE | 2 | 2 |

SIMPLE has only two endpoints; no separate stratum competence gate or generalization claim.

| Diagnostic subset | Correct endpoints | Exact pairs |
|---|---:|---:|
| SUFFICIENCY | 9/10 | 4/5 |
| CONTRADICTION | 11/12 | 5/6 |
| HISTORY | 1/4 | 0/2 |
| OBSERVATION | 4/4 | 2/2 |

Contradictory context subsets overlap; they are descriptive.

| Contradiction context | Correct | Total |
|---|---:|---:|
| current_mismatch | 3 | 3 |
| historical_mismatch | 4 | 4 |
| current_underdetermined | 3 | 3 |

| Pair | Gold A→B | Selected A→B | Changes | Tracks required transition | Exact pass |
|---|---|---|---|---|---|
| pro-v0-p01 | N→D | N→D | True | True | True |
| pro-v0-p02 | N→U | N→U | True | True | True |
| pro-v0-p03 | D→U | D→U | True | True | True |
| pro-v0-p04 | N→T | N→N | True | False | False |
| pro-v0-p05 | D→T | U→N | True | False | False |
| pro-v0-p06 | T→U | N→U | True | False | False |
| pro-v0-p07 | N→X | N→X | True | True | True |
| pro-v0-p08 | D→X | D→X | True | True | True |
| pro-v0-p09 | U→X | U→X | True | True | True |
| pro-v0-p10 | T→X | T→X | True | True | True |
| pro-v0-p11 | N→D | N→D | True | True | True |
| pro-v0-p12 | D→U | D→U | True | True | True |
| pro-v0-p13 | T→U | T→U | True | True | True |
| pro-v0-p14 | T→X | N→X | True | False | False |
| pro-v0-p15 | N→X | N→X | True | True | True |
| pro-v0-p16 | D→D | D→D | False | True | True |
| pro-v0-p17 | D→D | D→D | False | True | True |
| pro-v0-p18 | N→N | N→T | False | False | False |
| pro-v0-p19 | N→N | N→N | False | True | True |
| pro-v0-p20 | U→U | U→U | False | True | True |
| pro-v0-p21 | U→U | U→U | False | True | True |
| pro-v0-p22 | T→T | T→T | False | True | True |
| pro-v0-p23 | T→T | T→U | False | False | False |
| pro-v0-p24 | X→X | X→X | False | True | True |
| pro-v0-p25 | X→X | X→X | False | True | True |

## Integrity, scope and comparison

32 pre-inference checks passed, including synthetic full transport and scoring threshold tests; all 50 input objects satisfy the frozen schema. Independent witness validation recomputed every primitive and gold. Method/case hashes remained unchanged. Raw outputs were hashed, made read-only and committed before scoring. Zero-inference replay was byte-identical: `e3a1202ee1797a46a2ef2233e54b6929105e0a217301c786aa447f2a4efb7952`.

All 50 responses used separate requests and erased slots; zero retries, repairs or critics. Mean completion wall time 10.84s; total completion wall time 542.08s. No final answers were inspected during execution.

Freshness: 50 new IDs and distinct complete primitive objects, 25 newly constructed pairs; no prior output used in construction, no copied prior state object or diagnostic tuple. The primitive definitions and abstract truth combinations are intentionally reused; conceptual novelty is not claimed. The fixed scope legend only defines propositions. Witnesses, gold, proofs, tags and pair structure never enter prompts.

Preservation and publication audits accompany this report. Only this study adds paths; all inherited files, protected S/E source, prior heads and main are preserved. Full reachable-history credential/path scanning is required before push; private envelopes, reasoning, logs, authentication keys, signed streams and databases are excluded.

Published prior reduction results: Qwen 41/56, gpt-oss 42/56, Ministral 27/56. These are different datasets and input conditions. The new task supplies primitive conclusions and removes discovery. Comparison is qualitative; no causal improvement percentage is computed.

## Requested answers

1. **Can Qwen map an explicitly supplied correct primitive state?** Not established under the frozen endpoint gate: 43/50; each class is reported below. This statement is limited to supplied correct primitive states.

2. **Does it track minimal changes that should change diagnosis?** 11/15 exact changing pairs; fails the frozen 12/15 secondary requirement. Both endpoints and direction must be correct.

3. **Does it preserve diagnosis under irrelevant changes?** 8/10 exact stable pairs; passes the frozen 8/10 secondary requirement.

4. **Is sufficiency-to-ontology mapping reliable?** Sufficiency-only changes: 9/10 endpoints and 4/5 exact pairs. Other fields are held constant. This is a descriptive subset, not a separately registered reliability gate.

5. **Is contradiction precedence reliable?** Contradictory endpoints: 10/10. Consistency-toggle pairs: 5/6. Context-specific results appear below; no separate subset gate.

6. **Is historical/current composition reliable?** Historical class: 5/10; current defect: 9/10; no diagnosis: 9/10. Direct historical-composition pairs: 0/2. Temporal bindings were supplied explicitly.

7. **Does removing discovery change the observed boundary?** Removing discovery did not establish the registered reduction capability on these fresh cases. The changed dataset prevents an isolated causal comparison with prior studies.

8. **Reduction operator, upstream discovery/composition, or mixed?** The reduction operator itself remains unresolved even with upstream discovery removed. This does not show upstream difficulty is absent; the broader failure explanation remains mixed.

9. **What has not been demonstrated?** No raw-evidence diagnosis, primitive discovery, end-to-end diagnosis, generalization beyond these cases, autonomous Horus reasoning, learning, self-improvement, RSI, or internal causal mechanism has been demonstrated.

10. **Does this authorize a Horus architecture change?** No. This result itself authorizes no Horus architecture change. Publish and stop; any engineering consequence requires a separate decision.

