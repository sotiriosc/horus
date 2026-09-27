# Horus v0.2 grounded consequence learning

V0.2 adds one bounded model-weight learning path to the frozen v0.1 runtime.
The existing `dolphin-mixtral:latest` joint Map still supplies `next_state`.
A specialized Qwen consequence model supplies only `consequence`; mechanical
reconciliation and Explorer are unchanged. Neither model can execute an action
or authorize Memory.

```text
Mixtral joint request --------------------> next_state
                                                \
                                                 mechanical Map + Explorer
                                                /
Qwen base plus trained LoRA --------------> consequence
```

The consequence request contains only current state, target action alias, and
authenticated chronological history. It contains no joint response, joint
consequence, predicted next state, world law, future execution, or receipt.
Both complete Map requests are durably registered before either model returns.

## Grounded example boundary

`python -m horus.learn freeze` opens every source session through
`SessionStore`, which verifies its signed checkpoint and HMAC-chained streams.
For each example the builder requires:

- one authorized event paired with one authorized training record;
- matching receipt identity and provenance hashes;
- exact receipt-to-Memory agreement;
- exactly one request, response, and parsed consequence-call lifecycle;
- a registered consequence request independent of the joint response;
- a parsed prediction durably recorded before the realized event;
- exact reconstruction of the pre-execution state, selected action, and prior
  authenticated history; and
- a unique receipt and example identity.

It then derives `{"consequence": value}` from the original realized receipt.
No prediction or world rule supplies a target. Any failed check aborts dataset
construction.

The frozen manifest assigns complete sessions to train, validation, or heldout
evaluation before training. It binds ordered example IDs, request hashes,
receipt identities, targets, split assignments, base weights, and training
configuration. The checked-in dataset has 42 train, 6 validation, and 12
heldout examples from ten fresh six-step sessions.

## Model and adapter

The locally available `dolphin-mixtral:latest` artifact is a 26.4 GB quantized
GGUF intended for Ollama inference. It was not treated as a trainable weight
checkpoint. The fallback consequence role is the pinned open model
`Qwen/Qwen2.5-0.5B-Instruct` at revision
`7ae557604adf67be50417f59c2c2f167def9a775`. Its base weights remain unchanged.

Training optimizes a manual rank-8 LoRA over each `q_proj` and `v_proj`: 540,672
trainable parameters, alpha 16, dropout 0.05, AdamW at 0.0002, batch size 2,
gradient accumulation 2, five epochs/55 optimizer steps, weight decay 0.01,
and seed 20260925. The complete frozen settings are in
`horus/training_config.json`. The initial and final adapter files remain
side-by-side, and `models/horus_consequence_v0_2/learning-lineage.json` binds
the parent, dataset, settings, and result hashes.

Transformers resolves the exact pinned Qwen revision from the local Hugging
Face cache. An explicit snapshot directory can be supplied with
`--consequence-base-model`; it must contain the same base artifact used by the
adapter. The runtime deliberately does not download weights implicitly.

## Run the base and trained roles

An Ollama server with `dolphin-mixtral:latest` must be available at
`http://127.0.0.1:11434`. Use a new session directory outside the repository:

```sh
python -m horus.run --live --consequence-model base \
  --steps 6 --session /safe/private/path/base-demo

python -m horus.run --live --consequence-model trained \
  --trained-adapter models/horus_consequence_v0_2/trained-adapter.safetensors \
  --steps 6 --session /safe/private/path/trained-demo
```

If the pinned base snapshot is stored outside the standard cache, append:

```sh
--consequence-base-model /path/to/pinned-qwen-snapshot
```

The session directory holds the local authority key, raw model calls, and
signed streams and should remain private. The commands perform inference only;
they do not update weights automatically.

## Reproduce the bounded pipeline

The following commands are the implemented stages. Each output path must be
new, and collection/live session paths should be outside the repository.

```sh
python -m horus.learn collect --output /private/corpus --target 60 \
  --max-sessions 20 --steps-per-session 6
python -m horus.learn freeze --collection /private/corpus --output /private/dataset
python -m horus.learn evaluate --dataset /private/dataset \
  --output /private/pre.json
python -m horus.learn train --dataset /private/dataset \
  --pre-evaluation /private/pre.json --output /private/model
python -m horus.learn evaluate --dataset /private/dataset \
  --adapter /private/model/trained-adapter.safetensors \
  --output /private/post.json
python -m horus.learn compare --before /private/pre.json \
  --after /private/post.json --output /private/comparison.json
```

Collection and inference use a real local model and can be slow. The committed
artifacts record the completed run; reproducing them creates a distinct corpus
and trained artifact rather than extending the published one.

## Scope and trust boundary

The observed heldout change is small: accuracy rose from 50.0% to 66.7%, with
two correct predictions regressing. The 12-example heldout set is evidence of
this run, not a generalization claim. The environment is finite and repetitive,
the Qwen role differs from the original Mixtral consequence role, and no
independent replication has been run. The local HMAC key and files share one
host trust domain. Compromise of that domain, the Python process, or the
external execution implementation remains outside the claim.

No Explorer, next-state, reinforcement-learning, joint-training, or online
weight-update path is present. Explicit authenticated Memory and the learned
adapter coexist: history remains visible in later requests even after weights
change.
