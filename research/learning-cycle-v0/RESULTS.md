# Horus v0.3 learning-cycle result

## Decision

Generation 2 was **PROMOTED**. The cycle used the previously frozen
`continue-active` strategy: generation 1 initialized the candidate adapter,
and only 42 newly eligible training examples entered the optimizer. The active
reference moved atomically only after the candidate artifact, fresh-process
evaluation, provenance checks, leakage checks, and frozen promotion rule all
passed.

This is one bounded lifecycle result. The heldout set is small and strongly
repetitive; 12/12 should not be interpreted as general consequence-prediction
accuracy.

## Collection and split

The fixed collection used generation 1 and stopped at exactly 60 authorized
decisions across ten fresh six-step sessions. It made 180 unchanged joint
Mixtral calls and 180 generation-1 consequence calls. There were no retries,
abstentions, outcome-based extensions, or manufactured labels.

| Realized consequence | Count |
|---|---:|
| `-1` | 10 |
| `0` | 40 |
| `+1` | 10 |

The session-level split was 42 training, 6 validation, and 12 heldout. Heldout
contained two `-1`, eight `0`, and two `+1` examples. The fresh dataset
manifest SHA-256 is
`78368982a6c356cf0b816672e9be0e964f56479d184312c6108c05664fca8e8b`.
The incremental training manifest SHA-256 is
`d1db2a12ec7e5073e3cd236de9616649877280b5f3e57b22dec9c6eb43e0bb39`.

All targets were reconstructed from authorized original receipts after their
bound predictions. The registry usage map records each example's training,
validation, or evaluation role. No heldout identity entered the optimizer.

## Training lineage

| Field | Value |
|---|---|
| Generation | 2 |
| Parent generation | 1 |
| Strategy | `continue-active` |
| Parent adapter | `45a70d5f78aa98540ac00ca7e86a04155dd6a4c482a5f7d5dc6db25ed9f9c8fe` |
| Candidate adapter | `effb5eebef0649818c0697f1dfbadc73bc9e047eb1eaf6e3d5f6c63e0a35d39a` |
| Base weights | `fdf756fa7fcbe7404d5c60e26bff1a0c8b8aa1f72ced49e7dd0210fe288fb7fe` |
| Trainable parameters | 540,672 |
| Optimizer steps | 55 |
| Heldout examples seen by optimizer | 0 |

The initial generation-2 adapter hash exactly equals the generation-1 artifact
hash, proving the declared continuation parent. The final hash differs.
Training reused the frozen rank-8 LoRA configuration: alpha 16, dropout 0.05,
`q_proj`/`v_proj`, AdamW, learning rate 0.0002, batch 2, accumulation 2,
five epochs, weight decay 0.01, and seed 20260925. No hyperparameter search was
run.

Two incumbent evaluations and candidate evaluation ran as separate processes.
The promotion comparison used fresh process PIDs 235318 and 235727. A further
independent registry load in PID 235978 reconstructed generation 2 from disk
and reproduced its artifact hash exactly.

## Heldout comparison

| Metric | Generation 1 incumbent | Generation 2 candidate |
|---|---:|---:|
| Overall | 2/12 (16.7%) | 12/12 (100.0%) |
| `-1` | 0/2 (0.0%) | 2/2 (100.0%) |
| `0` | 0/8 (0.0%) | 8/8 (100.0%) |
| `+1` | 2/2 (100.0%) | 2/2 (100.0%) |
| Invalid | 0 | 0 |

Prediction transitions were 10 wrong-to-correct, zero correct-to-wrong, zero
unchanged-wrong, and two unchanged-correct.

The result differs from the historical v0.2 8/12 evaluation because this cycle
uses a new, separately frozen heldout set collected under generation 1. It does
not revise or replace the earlier result.

## Frozen promotion rule

Every condition passed:

- at least 12 heldout examples and at least two examples per class;
- strictly higher candidate accuracy;
- no increase in invalid responses;
- more wrong-to-correct than correct-to-wrong transitions;
- no accuracy drop greater than 0.50 for a class with at least three examples;
- provenance, artifact, fresh-reload, and optimizer-separation checks.

The rule SHA-256 is
`44991d3ebc09b29e0d658fa5d123d39540a408897a41eda6999d29fe1abc3892`.
The final registry state SHA-256 is
`d694c2e615a35747eb9a57555d2856595bff2ca4bd6adf14f413ad731fbeaf0a`.
Generation 0 and generation 1 are RETIRED; generation 2 is the sole ACTIVE
entry. No artifact was overwritten or deleted.

## Reproduction and operation

The committed evidence registry is directly inspectable:

```sh
python -m horus.learn history \
  --registry research/learning-cycle-v0/registry
```

Run Horus with the selected generation using a new private session and a local
Mixtral server:

```sh
python -m horus.run --live \
  --consequence-model active \
  --model-registry research/learning-cycle-v0/registry \
  --steps 10 --session /safe/private/runtime-session
```

For a new private lifecycle, initialize a separate registry, collect one fixed
batch, and invoke one cycle:

```sh
python -m horus.learn init-registry --registry /safe/private/horus-models
python -m horus.learn collect-active \
  --registry /safe/private/horus-models \
  --session-root /safe/private/horus-sessions \
  --target 60 --max-sessions 20 --steps-per-session 6
python -m horus.learn cycle \
  --registry /safe/private/horus-models \
  --session-root /safe/private/horus-sessions \
  --strategy continue-active
```

The cycle command creates at most one candidate. It does not collect, train, or
start the next generation automatically.

## Limitations

The environment is finite and generated highly repetitive trajectories: 40 of
60 new outcomes were `0`, and eight of twelve heldout targets were `0`.
Session separation prevents direct row leakage but does not make these short
trajectories semantically diverse. The `-1` and `+1` heldout classes had only
two examples each, so the catastrophic-class rule did not apply to those
classes. This run establishes safe candidate isolation, comparison, and atomic
selection. It does not establish broad generalization, autonomous recursive
improvement, causal understanding, or robustness outside the declared local
authority and host trust boundary.
