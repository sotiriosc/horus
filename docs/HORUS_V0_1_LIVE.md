# Horus v0.1 live runtime

Horus v0.1 adds model-backed prediction and real cross-process session restore
without changing the established receipt, Measure, authorization, Recovery, or
protected Memory implementation. The deterministic v0 command remains:

```sh
python -m horus.run
```

Start and resume a live session outside the repository:

```sh
python -m horus.run --live --steps 4 --session /safe/private/path/demo
python -m horus.run --live --steps 2 --session /safe/private/path/demo --resume
```

For each legal action, the live Map freezes two requests before invoking either
model path. The joint request uses the existing joint instruction and model
configuration; only its `next_state` is consumed. The consequence-only request
has the same state, action alias, and authenticated history, but an independent
system instruction and no joint response or predicted next state. Mechanical
reconciliation forms `(joint.next_state, consequence_only.consequence)`. Any
invalid component makes the decision abstain before execution.

The mechanical Explorer chooses a unique finite consequence maximum. Its
bounded tie behavior is unchanged: it can choose the first untried tied action
in canonical order, while a tie among tried actions abstains. Models remain
proposal sources. They cannot execute, mint a receipt, authorize a record, or
write protected Memory.

## Restore boundary

The session directory contains:

| File | Purpose |
|---|---|
| `authority.key` | 256-bit local application HMAC key, mode `0600` |
| `checkpoint.json` | Signed current state, runtime/epoch, progress, and exact stream heads |
| `events.jsonl` | HMAC-chained authorized receipt and Memory records |
| `model-calls.private.jsonl` | HMAC-chained exact request intents and raw responses |
| `training-records.jsonl` | HMAC-chained grounded prediction/target examples |
| `.lock` | Advisory single-writer process lock |

Every stream record binds its sequence number, predecessor hash, record kind,
content, and HMAC. The signed checkpoint binds the exact count and head of all
three streams. Missing provenance, content alteration, duplicate receipt
identity, broken ordering, or an uncommitted tail fails closed.

On resume, Horus verifies the checkpoint and all streams, creates a fresh
external receipt source and a fresh framework epoch, and imports old records as
detached read-only history. It does not recreate old Python receipt objects.
Each event records its source identity and originating runtime index, so
pre-restart records remain distinguishable from new receipts. Imported history
can affect Map proposals, but only a new original receipt passing the unchanged
framework can authorize a new publication.

This is application-local integrity. A party able to replace both the session
and `authority.key`, a compromised external simulation root, or hostile code in
the same process remains trusted/out of model. No physical, cryptographic
hardware, remote attestation, or source-capability continuity claim is made.

## Training records

One record is appended after each authorized execution. It includes session,
epoch, transaction and order identities; input and history hashes; selected
action; parsed joint and consequence-only responses; separate predicted and
realized values; match fields; receipt identity/provenance; authorization;
Memory event reference; and explicit prediction-versus-target labels. Raw
prompts and responses stay in the private call stream. A prediction is never
labelled as an authenticated target merely because the model produced it.

No weight update, reinforcement learning, model Explorer, or automatic
training occurs in v0.1.

The first bounded two-process run is recorded in the
[live demonstration report](HORUS_V0_1_LIVE_DEMONSTRATION.md).
