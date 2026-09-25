# Horus v0.3 consequence learning cycle

V0.3 turns the single v0.2 consequence-model update into a bounded lifecycle:

```text
ACTIVE consequence generation
→ fixed-size authenticated collection
→ session-separated frozen dataset
→ new candidate adapter
→ fresh-process incumbent/candidate evaluation
→ frozen promotion rule
→ atomic ACTIVE reference update or rejection
```

The joint Mixtral next-state role, mechanical Explorer, external execution,
receipt authorization, Recovery, and Memory semantics are unchanged. No other
role is trained and no event-triggered online optimization is present.

## Registry

Initialize a private registry once:

```sh
python -m horus.learn init-registry --registry /safe/private/horus-models
```

The imported registry starts with generation 0 as the frozen Qwen base and
generation 1 as the verified v0.2 adapter. It contains:

```text
active-model.json
states/state-<sha256>.json
generations/generation-0000/generation.json
generations/generation-0001/
  generation.json
  trained-adapter.safetensors
  learning-lineage.json
  evaluation.json
  example-usage.json
  dataset/{manifest.json,examples.jsonl}
```

Every JSON control document carries a canonical payload hash. Each immutable
state binds all generation manifests, statuses, parent generations, and
artifact hashes. `active-model.json` binds exactly one ACTIVE entry to one
immutable state snapshot. Artifact, lineage, evaluation, and usage hashes are
verified at load time. Paths are confined beneath the registry root.

Candidate work is written into a new generation directory while the active
reference remains unchanged. On completion, Horus writes a new immutable state
and atomically replaces only `active-model.json`. A crash before replacement
leaves the incumbent state authoritative. Rejected artifacts remain registered
and are never deleted.

This is local hash integrity, not hostile-host security. A party able to
replace code and consistently recompute every file remains inside the trusted
host boundary.

## Collection and cycle

Collect one fixed batch using the current ACTIVE generation:

```sh
python -m horus.learn collect-active \
  --registry /safe/private/horus-models \
  --session-root /safe/private/horus-sessions \
  --target 60 --max-sessions 20 --steps-per-session 6
```

Then stop runtime collection and run exactly one learning cycle:

```sh
python -m horus.learn cycle \
  --registry /safe/private/horus-models \
  --session-root /safe/private/horus-sessions \
  --strategy continue-active
```

The default `continue-active` strategy initializes the new LoRA tensors from
the incumbent adapter and optimizes only newly eligible training examples. It
gives the clearest parent-child lineage and avoids reinitializing already
learned parameters. The implemented alternative is explicit:

```sh
--strategy base-cumulative
```

That strategy initializes from frozen base Qwen and trains on the unique union
of prior non-rejected training examples and the new training split. It does not
silently mix with continuation. Both strategies evaluate on only the new
session-separated heldout requests.

Each example has a stable identity. Generation usage records distinguish
training, validation, and evaluation. Previously consumed sessions are
excluded from new eligibility. A partially consumed session fails closed, and
an example cannot appear in both optimizer and evaluation sets.

## Frozen promotion rule

The machine-readable rule is `horus/promotion_rule.json`. A candidate becomes
ACTIVE only when all conditions hold:

1. At least 12 heldout examples exist, with at least two examples for each of
   `-1`, `0`, and `+1`.
2. Candidate overall accuracy is strictly greater than incumbent accuracy on
   the exact same requests.
3. Invalid responses do not increase.
4. Wrong-to-correct transitions exceed correct-to-wrong transitions.
5. For a class represented by at least three heldout examples, accuracy does
   not decrease by more than 0.50 absolute.
6. Provenance, optimizer separation, artifact hashes, and fresh-process reload
   checks all pass.

The rule is frozen before the first generation-2 collection and evaluation. A
training-loss decrease has no promotion authority. Insufficient evidence or
any failed condition rejects the candidate and leaves the incumbent ACTIVE.

## Use the selected model

```sh
python -m horus.run --live \
  --consequence-model active \
  --model-registry /safe/private/horus-models \
  --steps 10 --session /safe/private/runtime-session
```

Startup verifies the active reference, state, lineage, and adapter hash before
loading. The command prints generation, parent generation, and artifact hash.
Every consequence request and its later receipt-linked training record retain
the generation, base-model identity, artifact hash, and adapter identity.

View the durable history with:

```sh
python -m horus.learn history --registry /safe/private/horus-models
```

Each `cycle` invocation creates at most one candidate generation. It never
starts another generation automatically.
