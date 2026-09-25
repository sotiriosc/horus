# Grounded consequence learning v0.2 results

## Result

The bounded learning chain completed. Sixty authorized executions produced
sixty receipt-grounded examples across ten fresh sessions. A rank-8 LoRA for
the specialized Qwen consequence role was optimized on 42 examples and loaded
from disk in a fresh process. On the frozen 12-example heldout split, accuracy
changed from 6/12 (50.0%) to 8/12 (66.7%). This is a real parameter-update and
integration result; the small evaluation does not establish broad predictive
quality.

| Metric | Base | Trained |
|---|---:|---:|
| Overall | 6/12 (50.0%) | 8/12 (66.7%) |
| Realized `-1` | 0/4 (0.0%) | 2/4 (50.0%) |
| Realized `0` | 0/2 (0.0%) | 2/2 (100.0%) |
| Realized `+1` | 6/6 (100.0%) | 4/6 (66.7%) |
| Invalid | 0 | 0 |

The comparison contains four wrong-to-correct cases, two correct-to-wrong
regressions, two unchanged-wrong cases, and four unchanged-correct cases. Every
individual input identity, target, before prediction, and after prediction is
preserved in `evaluation-comparison.json`.

The regressions are:

| Example ID | Target | Base | Trained |
|---|---:|---:|---:|
| `49e7f084b481f429ebae616a30822e2dc973694b0da54af3d450309f6b6663b6` | +1 | +1 | -1 |
| `e95ab5d9babc2aea7713e547e64d51ddf20b330a1aecd0999da02e98659b3eb2` | +1 | +1 | -1 |

The four corrections were two `+1 → -1` changes with realized target `-1` and
two `+1 → 0` changes with realized target `0`. The result was accepted without
hyperparameter tuning or a second training configuration.

## Corpus and split

Collection made exactly 360 model calls: 180 unchanged Mixtral joint calls and
180 base-Qwen consequence calls. All 60 selected actions executed and produced
authorized original receipts. The realized distribution was 20 `-1`, 10 `0`,
and 30 `+1`. The frozen session-level split was:

| Split | Examples | `-1` | `0` | `+1` |
|---|---:|---:|---:|---:|
| Train | 42 | 14 | 7 | 21 |
| Validation | 6 | 2 | 1 | 3 |
| Heldout | 12 | 4 | 2 | 6 |

The examples file SHA-256 is
`3672a2f4a151c7042acb74882104629f277216a529c83aeb5634c6b5d9a931e3`.
The dataset manifest identity is
`4195c5b21aeeccb02d3a51d44277cd498901144770233d11d51713af94b0fcd3`.
No heldout example was exposed to the optimizer.

## Parameter and lineage proof

The inspected host had an NVIDIA GeForce RTX 4090 with 24 GB VRAM, 62 GiB
system RAM, and approximately 71 GB free workspace storage. PyTorch
2.5.1+cu121 and Transformers 5.14.1 were available with CUDA; PEFT,
Accelerate, and bitsandbytes were not installed. The existing Ollama Mixtral
weight blob was 26,441,544,128 bytes with SHA-256
`bdb11b0699e03d791f0accd97279989d810d79615c6cf5ac21fb68e8f33e8ca3`.
It was a quantized inference GGUF, so this run did not represent it as a
trainable full-precision or adapter-compatible checkpoint.

The trained base was `Qwen/Qwen2.5-0.5B-Instruct` revision
`7ae557604adf67be50417f59c2c2f167def9a775`. The immutable base-weight SHA-256
was `fdf756fa7fcbe7404d5c60e26bff1a0c8b8aa1f72ced49e7dd0210fe288fb7fe`.
Base weights were frozen; 540,672 adapter parameters changed during 55 AdamW
steps.

| Artifact | SHA-256 |
|---|---|
| Initial adapter | `c80867dee0dfa77086faf4c5bc1409a17c07a0fa420e4bae08bcc2989cd554b8` |
| Final adapter | `45a70d5f78aa98540ac00ca7e86a04155dd6a4c482a5f7d5dc6db25ed9f9c8fe` |

Validation loss was 0.352096 before training and 0.060349 after the final
epoch. Post-training evaluation ran in fresh process PID 155883 after loading
the final adapter from disk. The durable lineage is
`models/horus_consequence_v0_2/learning-lineage.json`.

Two implementation failures are disclosed in the model directory. The first
failed before any optimizer step because new adapter tensors were on CPU while
the base was on CUDA. The second completed 55 steps but failed while serializing
metadata; it was declared ineligible before heldout post-evaluation. A clean,
separately initialized replacement completed under the frozen configuration
and produced the reported adapter. Neither failed run was used for evaluation
or integration.

## Controlled decision and live integration

On one frozen state-1, empty-history context, the base model predicted `+1` for
ADVANCE, HOLD, and RETREAT, so Explorer used its bounded untried tie fallback
and selected ADVANCE. The trained model predicted `0`, `+1`, and `0`, producing
a unique HOLD maximum. Neither comparison path executed, minted a receipt, or
published Memory. The parameter artifact was the only model-side difference.

The production trained path then ran a fresh six-step Horus session. It made 36
real model calls and authorized all six original receipts. Its first decision
matched the controlled trained result and selected HOLD. Subsequent requests
contained authenticated chronological observations, demonstrating that weight
learning did not erase explicit Memory. No training occurred during the demo.

The public-safe replay evidence is in `trained-demo-summary.json`; private raw
calls and the local session authority remain outside the repository.

## Limitations

The evaluation contains only twelve examples from two sessions in a small
deterministic environment. The trained role is a smaller specialized fallback
because the available quantized Mixtral GGUF was not a legitimate trainable
checkpoint with the installed tooling. Two heldout positive cases regressed.
The comparison establishes that parameters can change forecasts and a
mechanical decision on one identical pre-execution context; it does not claim
general causal understanding, robust generalization, or improved end-to-end
reward. Integrity remains bounded by the existing local host, authority key,
execution source, and Python-process trust assumptions.
