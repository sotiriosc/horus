# Horus Causal Machine Learning v0

Cycle 1: **CAUSAL_WORLD_MODEL_LEARNING_NOT_ESTABLISHED**. Cycle 2 was not run because the first-cycle gate did not authorize it.

This is an externally orchestrated, bounded deterministic causal-machine experiment. C0 is the exact successful prior M1 adapter plus the unchanged Qwen3-14B base, not M2. It reproduced the prior temporal result at 540/540 before this study. No active adapter was promoted and this study does not establish RSI.

## Provenance and prospective design

Branch: `research/horus-causal-machine-learning-v0`. Base: `9e53191f2d1a22aadb0264ab91ca929479225fec`. Method Freeze: `80ba6dbe2a8a4997f87c3d4e78dd5683552d97e4`. World/Data Freeze: `9a6469fc42b3579cd4dec8ecc6c37e262bb5c95f`. Simulator/DSL SHA256: `f6f1f9e0b89701bb2d7464259bbd24d392795d385d7963cb826502c081cd8101`.

C0: Qwen/Qwen3-14B@231c69a380487f6c0e52d02dcf0d5456d1918201 + adapter `ba679e10cac31b5b17c8589c0740d74ac98c2db1882d7edd39419cb9110a0b01`. Base shard and tokenizer hashes are in `handoff.json` and the unchanged prior upstream manifest.

Per cycle: 960 H, 240 V, 480 T, 40 sealed control machines. All 3,440 worlds and both cycles were frozen before causal inference. Each H/V/T world has one scheduled scored endpoint following 64 executed diagnostic context actions; diagnostic context is never a training target. Total prospective diagnostic actions: 220,160. Primary endpoints: 3,360 if both cycles execute. Each arm can execute up to 160 control actions per cycle. See actual phase receipt counts below.

Global seed: 20261001; pool seed bases: `{"H1":30261001,"H2":70261001,"T1":50261001,"T2":90261001,"U1":60261001,"U2":100261001,"V1":40261001,"V2":80261001}`. Each accepted case records its exact candidate seed. Sixteen diagnostic schedules are fixed in the materialized manifest.

The finite declared hypothesis family is the Cartesian product of 4,632 sensor roots. The independent recursive checker exhaustively filters it using visible histories and rejects ambiguity. The model sees only opaque port names, observed interventions and a candidate action. Hidden programs, states, graphs, oracle labels and family names are excluded from prompts and the planner. Whole-machine normalized graph, exact behavioral equivalence, seed, history and endpoint overlaps are zero across all pools. Test/control machines have strictly larger component/depth/delay/state counts within each corresponding family. Primitive motifs and generator templates remain shared; this is not arbitrary-logic transfer or proof against all template learning.

## Raw-first evidence

- `evaluation1-raw-freeze.json`: `52d0a3dc9943d9abb5c478784b2d9182a56a11bf`
- `harvest1-raw-freeze.json`: `1dc9b62c03b0ed989bfcaa59f091ccc510327bf9`
- `incumbent-reproduction-raw-freeze.json`: `6b2ae556309962f4bf56d7d6dd48505623ccbae0`

Actual execution and request counts (excluding the initial diagnostic context and incumbent reproduction):

| Phase | Causal prediction calls | Actual scored executions | Unexecuted control alternatives |
|---|---:|---:|---:|
| harvest1 | 1200 | 1200 | 0 |
| evaluation1 | 2084 | 1241 | 843 |

## Cycle 1

Harvest errors E1: 783/960; D1: `{"causal_correct_replay":783,"causal_error":783,"prior_temporal_training_replay":512}` = 2078 exposures/epoch. Every authenticated error was admitted. Correct replay uses replacement; counts are exposures, not additional unique machines. No unexecuted causal alternatives or hidden-program targets entered training.

C1 continued C0. Initial adapter SHA256 `ba679e10cac31b5b17c8589c0740d74ac98c2db1882d7edd39419cb9110a0b01`; final `9e80029c33e9c0bbfa394be2d5a88de076c70747e57cdd1369b1ad324cb17136`. Base unchanged: True; adapter changed: True; trainable parameters 64,225,280; epochs 2; optimizer steps 520; examples seen 4156; training seconds 19673.24; peak allocated GiB 14.562. Save/reload exact: True. Loss, gradient, validation, recovery and memory records are in the artifact manifest.

Prediction exact: **249/480 → 273/480**, gain **+5.00pp**, exact paired two-sided McNemar p=0.0353236825. Paired table: both correct 201, incumbent-only 48, candidate-only 72, both wrong 159. Bit accuracy: 84.06% → 87.34%. Schema: 480/480 → 480/480.

### family

| Stratum | Incumbent | Candidate | Gain pp |
|---|---:|---:|---:|
| conditional_delay | 56/160 | 72/160 | +10.00 |
| delayed_combination | 94/160 | 95/160 | +0.62 |
| input_gated_delay | 99/160 | 106/160 | +4.38 |

### causal_depth

| Stratum | Incumbent | Candidate | Gain pp |
|---|---:|---:|---:|
| 6 | 2/7 | 4/7 | +28.57 |
| 7 | 109/221 | 115/221 | +2.71 |
| 8 | 138/252 | 154/252 | +6.35 |

### delay_length

| Stratum | Incumbent | Candidate | Gain pp |
|---|---:|---:|---:|
| 3 | 249/480 | 273/480 | +5.00 |

### hidden_components

| Stratum | Incumbent | Candidate | Gain pp |
|---|---:|---:|---:|
| 12 | 249/480 | 273/480 | +5.00 |

Control: **8/40 → 11/40**, paired p=0.453125; classification **CAUSAL_CONTROL_BENEFIT_NOT_ESTABLISHED**. Each arm's mean actions conditional on success: 2.0 → 1.9090909090909092; common-success means (6 worlds): 2.0 → 1.5. Cumulative actual selected-action prediction errors: 79 → 61. Per-world failure modes appear in the control score files. The planner is fixed depth-one/width-four/Hamming/tie-order/budget-four; this claim is separate from prediction learning.

Prior temporal retention: **540/540**, schema **540/540**, loss 0.00pp. The frozen criterion requires >=530 exact and 540 valid.

Gate checks:

- exact_gain_at_least_10pp: FAIL
- paired_p_less_than_001: FAIL
- at_least_three_families_improve: PASS
- no_major_stratum_regression: PASS
- schema_at_least_99percent: PASS
- adapter_changed: PASS
- base_unchanged: PASS
- leakage_and_oracle_boundary: PASS
- temporal_retention: PASS
- temporal_schema_unchanged: PASS

Registered classification: **CAUSAL_WORLD_MODEL_LEARNING_NOT_ESTABLISHED**.

## Interpretation and descriptive checks

Unlike the prior temporal task, which applied one fixed global proposition/aggregation rule, each machine here has a different hidden dynamical program. The intended capability is to use executed intervention history to predict that unfamiliar system. The present result does not establish the full registered capability.

A posthoc, zero-inference persistence reference (predict the last observed sensor state, ignoring the action) scored 264/480, versus C1 at 273/480. This reference was not preregistered and changes no gate. It shows that much of the test can be answered by persistence; the small advantage over it is insufficient to claim robust causal inference. See `descriptive-results.json` for per-sensor-position counts and frozen target distributions.

Structural complexity did not guarantee higher measured difficulty: C0 scored 177/960 (18.44%) on H1 and 249/480 (51.88%) on the larger T1 machines. The distributions differ in compositions and resulting behavior; do not interpret the larger structures as uniformly harder empirical cases. Whole-machine disjointness excludes exact case reuse, while shared motifs and local persistence remain possible explanatory shortcuts.

Control used 144 actual actions for C0 and 137 for C1. Failures were action-budget exhaustion: 32/40 for C0 and 29/40 for C1. Neither arm selected a schema-invalid prediction.

## Completion questions

1. **Did C0 learn a causal prediction capability from executed mistakes?** The registered causal prediction learning claim was not established; the measured changes and failed gates above define the result.

2. **Did that improvement generalize to structurally unseen machines?** Structurally held-out performance was measured, but the full registered learning claim was not established.

3. **Did improved prediction produce better goal-directed control?** The registered control benefit was not established.

4. **Did C1 preserve the prior temporal capability?** Yes.

5. **Did C1 encounter genuinely new errors in the harder Cycle-2 family?** Not tested; Cycle 2 did not proceed.

6. **Did C2 learn from those errors?** Not tested.

7. **Did C2 preserve Cycle-1 gains?** Not tested.

8. **Is the improvement distinguishable from exact/template memorization?** Exact program/behavior/history memorization is excluded by structural disjointness. Shared primitive motifs and generator templates remain, so this cannot exclude all template-based learning.

9. **What exact new capability is established?** No new causal-learning capability met the full registered gate. Engineering qualification and authenticated execution are demonstrated separately.

10. **What still separates this system from RSI?** Horus did not autonomously diagnose a limitation, propose/predict an intervention, obtain authorization, build and promote a verified improvement, then repeat as the improved system. The external experiment supplies orchestration; even a positive result would not establish RSI.

## Audits and boundaries

Raw evidence was committed before scoring, matched receipt bundles authenticate executed targets, and post-campaign scoring reproduced byte-identical outputs with zero inference. Exact prompts and generated token decoding were independently checked. All inherited files and prior local/remote branch heads are preserved. Secret-free reachable-history audit precedes publication. Private world state, raw signed streams, authority key, raw model output, adapters and optimizer/recovery binaries remain local. No merge, architecture/model promotion, next study or additional scientific campaign follows this result.
