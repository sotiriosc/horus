# Qwen Error-Driven QLoRA Learning v0

Registered Cycle-1 result: **ERROR_DRIVEN_PARAMETER_LEARNING_SUPPORTED**.

Registered Cycle-2 result: **SECOND_LEARNING_CYCLE_NOT_ESTABLISHED**.

## Frozen identity

Branch: `research/qwen-error-driven-qlora-learning-v0`. Base `379912673e692c7b4b7c28aa5b3a17b2bffbc0d3`. Method Freeze `9024f4effbea4bfe06f8af393032fb25837964e4`. Data/Split Freeze `d8636db079aeaf5b86a5032275dd2e0ab9151b95`.

All arms use `Qwen/Qwen3-14B@231c69a380487f6c0e52d02dcf0d5456d1918201` in the same HF/NF4 stack: BF16 quantized compute, double quantization, native nonthinking template, greedy decoding, context 1536, max new tokens 96, batch 4. M0 disables the adapter; M1/M2 enable the learned adapter. No GGUF/HF outcome comparison enters any gate.

LoRA r16/alpha32/dropout0/all-linear across 280 projections; 64,225,280 trainable parameters. Two fixed epochs, microbatch 1, accumulation 8, AdamW lr 1e-4, 5% warmup then linear decay. Final adapter only; validation loss is diagnostic. Complete package lock, GPU/CUDA identity and resource measurements are in `engineering-qualification.json`; exact settings in `runtime-settings.json`; upstream hashes/template identity in `upstream-provenance.json`.

Synthetic qualification passed in 265.1 seconds; peak allocated GPU memory 15.61 GiB. An earlier pre-scientific attempt was interrupted by a reported freeze/restart; the cause was not established. Recovery reduced engineering context, capped allocations and added a resource watchdog before Method Freeze. No scientific outcomes informed these choices.

## Prospective data

| Pool | Cases | Prior counts |
|---|---:|---|
| H1 | 1980 | 2, 3, 4, 5, 6, 7 |
| V1 | 360 | 2, 3, 4, 5, 6, 7 |
| T1 | 540 | 8, 9 |
| R1 | 360 | 1, 2, 3, 4, 5, 6, 7 |
| H2 | 1980 | 10, 11, 12 |
| V2 | 360 | 10, 11, 12 |
| T2 | 540 | 13, 14, 15 |
| R2 | 360 | 10, 11, 12 |

Both cycles and all counterfactuals were generated before M0. Each test has 60 cases per joint output. The sealed prior-count ranges appear in neither harvest/validation/regression/neighbor pool. Ordering and package consistency cannot evade the normalized leakage checks. Abstract truth patterns and the existential operation recur; this is bounded synthetic length/composition generalization, not a new logical operation or general real-task competence.

## Cycle 1

Harvest: 969/1980 verified joint errors; all were admitted. D1: {'error': 969, 'counterfactual': 1766, 'correct_replay': 969}, totaling 3704 exposures per epoch and 3287 unique case IDs. Wrong answers were never supplied in training prompts.

M1 initial adapter SHA256 `05a49580e58338827c11c149bf829968c6f650f32212c0fa748f0f6bc6da09b4`; final `ba679e10cac31b5b17c8589c0740d74ac98c2db1882d7edd39419cb9110a0b01`. Adapter freeze commit `6ed70c9b57f04b44d1febd0237bd232a61ab4f92` precedes sealed-test inference. Base unchanged: True; adapter changed: True; save/reload exact: True.

Training: 926 updates; 7408 effective example exposures; 13.4 minutes; peak allocated 14.55 GiB; adapter 256,976,504 bytes. Validation losses: [{'after_epoch': 0, 'mean_loss': 0.4094919960389638}, {'after_epoch': 1, 'mean_loss': 5.482292164144593e-06}, {'after_epoch': 2, 'mean_loss': 3.59838327592183e-06}]. Full training loss, gradients, learning-rate schedule and parameter fingerprints are preserved in the artifact manifest. Adapter/optimizer binaries remain in persistent local research storage, referenced by hashes; no deployment occurred.

M1 training had two interruptions: a user-reported restart after logged update 256, resumed at checkpoint 250, and a GPU telemetry command failure after update 913, resumed at checkpoint 900. The unchanged watchdog terminated training on the second interruption. The frozen recovery mechanism recomputed 19 logged completed updates (152 exposures). The initial adapter tensor file remained byte-identical; the JSON configuration differed only in target-module list ordering, with identical normalized contents and the same verified 280 projections. The duration above covers the resumed process only; combined recorded active training duration was at least 362.0 minutes, excluding downtime/unlogged work. Effective trajectory: 926 updates; at least 945 physical completed updates including discarded work. No recipe, data, candidate-selection or sealed-evaluation rule changed.

Mean training loss per example by epoch: 1: 0.011010167, 2: 1.670907e-06. These teacher-forced engineering diagnostics do not substitute for sealed inference.

The M1 peak allocated-memory figure above covers the final resumed process only. The complete-stage resource audit reports sampled device headroom across all recorded processes; those device samples are not equivalent to a continuous PyTorch allocation maximum.

| Metric | M0 | M1 | Change |
|---|---:|---:|---:|
| joint | 208/540 (38.52%) | 540/540 (100.00%) | +61.48 pp |
| current_violation | 455/540 (84.26%) | 540/540 (100.00%) | +15.74 pp |
| prior_violation | 250/540 (46.30%) | 540/540 (100.00%) | +53.70 pp |
| schema | 540/540 (100.00%) | 540/540 (100.00%) | +0.00 pp |
| targeted | 170/419 (40.57%) | 419/419 (100.00%) | +59.43 pp |

Paired T1 table: both correct 208; incumbent only 0; candidate only 332; both wrong 0. Two-sided exact McNemar p=2.2859748e-100. The p-value follows the registered paired-endpoint test; it does not establish generalization beyond this synthetic generator.

| Family | Metric | Incumbent | Candidate | Change |
|---|---|---:|---:|---:|
| clear_YES | joint | 30/120 (25.00%) | 120/120 (100.00%) | +75.00 pp |
| clear_NO | joint | 12/60 (20.00%) | 60/60 (100.00%) | +80.00 pp |
| contradiction_independent | joint | 37/182 (20.33%) | 182/182 (100.00%) | +79.67 pp |
| current_determinate | current_violation | 287/360 (79.72%) | 360/360 (100.00%) | +20.28 pp |
| all_prior_determinate | prior_violation | 72/185 (38.92%) | 185/185 (100.00%) | +61.08 pp |
| schema | schema | 360/360 (100.00%) | 360/360 (100.00%) | +0.00 pp |

R1 families were prospective intended strength probes. Several M0 family scores were low in this HF stack, so their labels do not establish strong baseline competence; the table reports the actual baseline. Both arms were schema-valid on every T1 case, so the observed T1 gains are semantic improvements rather than schema repair.

### Descriptive error decomposition

These posthoc subsets do not alter any gate or candidate.

| Subset | Metric | M0 | M1 |
|---|---|---:|---:|
| current_UNKNOWN | current_violation | 140/180 | 180/180 |
| prior_UNKNOWN | prior_violation | 180/180 | 180/180 |
| mixed_prior_aggregation | prior_violation | 183/355 | 355/355 |

Gate checks:

- joint_gain_at_least_8pp: PASS
- paired_p_less_than_001: PASS
- targeted_gain_at_least_10pp: PASS
- schema_at_least_99percent: PASS
- no_major_regression: PASS
- noncollapsed: PASS
- adapter_changed: PASS
- base_unchanged: PASS
- leakage: PASS

Registered classification: **ERROR_DRIVEN_PARAMETER_LEARNING_SUPPORTED**. Leakage audit: PASS; exact, normalized and package-ignored sealed overlaps are all zero. Abstract family overlap counts: {'T1/H1': 17, 'T1/H2': 17, 'T2/H1': 18, 'T2/H2': 18}.

## Cycle 2

Harvest: 3/1980 verified joint errors; all were admitted. D2: {'error': 3, 'counterfactual': 6, 'correct_replay': 3, 'cycle1_retained_replay': 512}, totaling 524 exposures per epoch and 408 unique case IDs. Wrong answers were never supplied in training prompts.

M2 initial adapter SHA256 `ba679e10cac31b5b17c8589c0740d74ac98c2db1882d7edd39419cb9110a0b01`; final `309d15f606e9f2c21bedf328d88705b72bacb9d1d49d3aa0198ce7f978ec4e3a`. Adapter freeze commit `9e91c4ef34b8ed87a93b10068bbbe9e76f3ab88a` precedes sealed-test inference. Base unchanged: True; adapter changed: True; save/reload exact: True.

Training: 132 updates; 1048 effective example exposures; 83.8 minutes; peak allocated 14.78 GiB; adapter 256,976,504 bytes. Validation losses: [{'after_epoch': 0, 'mean_loss': 2.102672018269796e-05}, {'after_epoch': 1, 'mean_loss': 1.404828310087098e-06}, {'after_epoch': 2, 'mean_loss': 1.1770318211078311e-06}]. Full training loss, gradients, learning-rate schedule and parameter fingerprints are preserved in the artifact manifest. Adapter/optimizer binaries remain in persistent local research storage, referenced by hashes; no deployment occurred.

Mean training loss per example by epoch: 1: 0.00026746205, 2: 7.0017789e-07. These teacher-forced engineering diagnostics do not substitute for sealed inference.

| Metric | M1 | M2 | Change |
|---|---:|---:|---:|
| joint | 540/540 (100.00%) | 540/540 (100.00%) | +0.00 pp |
| current_violation | 540/540 (100.00%) | 540/540 (100.00%) | +0.00 pp |
| prior_violation | 540/540 (100.00%) | 540/540 (100.00%) | +0.00 pp |
| schema | 540/540 (100.00%) | 540/540 (100.00%) | +0.00 pp |
| targeted | 420/420 (100.00%) | 420/420 (100.00%) | +0.00 pp |

Paired T2 table: both correct 540; incumbent only 0; candidate only 0; both wrong 0. Two-sided exact McNemar p=1. The p-value follows the registered paired-endpoint test; it does not establish generalization beyond this synthetic generator.

M1 was already correct on all T2 endpoints, leaving no measured headroom for the registered four-point improvement. Both incremental-gain gates fail unchanged. M2 received only three newly verified H2 errors (all prior YES predicted UNKNOWN), so this result establishes neither a second sealed improvement nor inability to learn again on a different, separately authorized task.

### T1 retention

| Metric | M1 | M2 | Change |
|---|---:|---:|---:|
| joint | 540/540 (100.00%) | 540/540 (100.00%) | +0.00 pp |
| current_violation | 540/540 (100.00%) | 540/540 (100.00%) | +0.00 pp |
| prior_violation | 540/540 (100.00%) | 540/540 (100.00%) | +0.00 pp |
| schema | 540/540 (100.00%) | 540/540 (100.00%) | +0.00 pp |
| targeted | 419/419 (100.00%) | 419/419 (100.00%) | +0.00 pp |

### R1 retention

| Family | Metric | Incumbent | Candidate | Change |
|---|---|---:|---:|---:|
| clear_YES | joint | 120/120 (100.00%) | 120/120 (100.00%) | +0.00 pp |
| clear_NO | joint | 60/60 (100.00%) | 60/60 (100.00%) | +0.00 pp |
| contradiction_independent | joint | 182/182 (100.00%) | 182/182 (100.00%) | +0.00 pp |
| current_determinate | current_violation | 360/360 (100.00%) | 360/360 (100.00%) | +0.00 pp |
| all_prior_determinate | prior_violation | 185/185 (100.00%) | 185/185 (100.00%) | +0.00 pp |
| schema | schema | 360/360 (100.00%) | 360/360 (100.00%) | +0.00 pp |

### R2 regression

| Family | Metric | Incumbent | Candidate | Change |
|---|---|---:|---:|---:|
| clear_YES | joint | 120/120 (100.00%) | 120/120 (100.00%) | +0.00 pp |
| clear_NO | joint | 60/60 (100.00%) | 60/60 (100.00%) | +0.00 pp |
| contradiction_independent | joint | 176/177 (99.44%) | 177/177 (100.00%) | +0.56 pp |
| current_determinate | current_violation | 360/360 (100.00%) | 360/360 (100.00%) | +0.00 pp |
| all_prior_determinate | prior_violation | 142/142 (100.00%) | 142/142 (100.00%) | +0.00 pp |
| schema | schema | 360/360 (100.00%) | 360/360 (100.00%) | +0.00 pp |

Gate checks:

- joint_gain_at_least_4pp: FAIL
- paired_p_less_than_005: FAIL
- t1_retention_loss_at_most_2pp: PASS
- no_major_regression: PASS
- schema_at_least_99percent: PASS
- adapter_changed: PASS
- base_unchanged: PASS
- leakage: PASS

Registered classification: **SECOND_LEARNING_CYCLE_NOT_ESTABLISHED**. Leakage audit: PASS; exact, normalized and package-ignored sealed overlaps are all zero. Abstract family overlap counts: {'T1/H1': 17, 'T1/H2': 17, 'T2/H1': 18, 'T2/H2': 18}.

## Completion questions

1. **Did trainable parameters actually change?** Yes for the scientific adapter(s); initial/final tensor fingerprints and artifact hashes differ.

2. **Did base weights remain frozen?** Yes: all loaded base parameters, buffers and NF4 quantization states matched before and after each completed scientific training cycle.

3. **Did M0 mistake training improve unseen M1 behavior?** M1 changed sealed T1 joint accuracy by +61.48 points (exact paired p=2.2859748e-100); the full registered learning claim passed.

4. **Did targeted errors improve?** The fixed UNKNOWN/aggregation subset changed by +59.43 points. Field and family results above define the scope of that observation.

5. **Did existing strengths survive?** The no-major-regression gate passed; interpret it using the measured baseline scores, since not every intended strength probe was strong for M0.

6. **Is the improvement distinguishable from memorization/leakage?** No sealed normalized state entered training or replay. Held-out prior counts test composition beyond the harvest lengths; recurring templates and abstract logic remain shared, so broad transfer or absence of all memorization is not established.

7. **Did M2 learn from M1’s own mistakes?** M2 parameters were updated from every verified M1 H2 mistake, with fixed neighbors and replay. Further sealed behavioral improvement was not demonstrated when both models reached 540/540; its second-cycle gate did not pass.

8. **Did M2 retain M1’s gains?** T1 retention changed by +0.00 points; registered retention gate passed.

9. **What exact capability is established?** One-cycle externally supervised error-driven parameter learning on this bounded synthetic task; a second-cycle success is not established.

10. **What separates this from RSI?** RSI still requires useful real tasks, authenticated consequences, autonomous diagnosis and bounded change proposals with predictions, protected authorization, implementation, sealed real-task validation, retention and repetition by the improved system. This externally designed pipeline establishes none of that autonomy.

## Preservation and publication boundary

Inherited published files and prior refs are unchanged; the promoted selector, Memory, grounded state, policy and main were not modified. The external restart cleared temporary worktrees/private files, whose recovery is not claimed. The earlier Qwen2.5-0.5B lineage and source remain intact; no historical scientific training examples were reused. Dolphin/Mixtral remains historical inference-only evidence. See `replay-audit.json`, `preservation-audit.json` and the publication audit.

Only the audited research branch is published. No merge, promotion, active-model replacement, policy modification, external deployment, RL or subsequent study occurs.
