# Composition empty-history schema contract v0

**SCHEMA-CONTRACT EFFECT SUPPORTED.** Exactly 18 real calls: original instruction
A 0/9 valid; explicit contract B 9/9. All nine pairs improve, zero reverse;
O1 0/4 → 4/4 and O2 0/5 → 5/5. All eight frozen gates pass. Original-contract
all-nine schema failure replicates; only 3/9 A raw strings exactly match history.
This tests schema compliance only. No world execution or correctness scoring.
Historical composition-v1 remains **C — NOT ESTABLISHED**.

Read the [27-section results report](../../research/composition-empty-history-schema-contract-v0-results.md),
[preregistration](../../research/composition-empty-history-schema-contract-v0-preregistration.md),
[compact results](results.json) and [executed verification](verification.json).

From repository root, use the retained private `real` evidence directory and a
fresh external output directory:

```sh
python3 -m experiments.composition_empty_history_schema_contract_v0.verify --registration "$SCHEMA_EVIDENCE/registration.json"
python3 -m experiments.composition_empty_history_schema_contract_v0.run --replay "$SCHEMA_EVIDENCE" --output "$SCHEMA_REPLAY"
```

These commands require no model/server or network and perform zero inference.
Replay reapplies the unchanged parser and requires all five files byte-identical:
`registration.json`, `metadata.json`, `attempted-requests.jsonl`, `model-calls.jsonl`,
`results.json`. Exact system/user bytes, original contexts/mappings/actions/seeds,
requests, raw responses, parser results and shape categories remain private.
The public compact result is an exact copy of the real/replay summary. The frozen
registration includes every experiment Python source hash and original input
archive digests; verification rejects altered sources or paired user payloads.

Five post-study preservation replays and exact command templates are recorded in
`verification.json`: composition-v1, forensic diagnosis-v0, input-bindings-v1,
Map-v0, established-prior Map-v1. All 26 regenerated historical files are identical.
No unrelated historical campaign was rerun.

The original archived registration/live interface is documented for reproducibility,
**not permission for another model campaign**:

```sh
python3 -m experiments.composition_empty_history_schema_contract_v0.run --register "$COMPOSITION_EVIDENCE" --output "$REGISTRATION_OUTPUT"
python3 -m experiments.composition_empty_history_schema_contract_v0.run --live --registration "$REGISTRATION_OUTPUT/registration.json" --proof "$MODEL_BYTE_PROOF" --output "$LIVE_OUTPUT"
```

A new authorized run would first need full hashing of the frozen manifest and
all referenced blobs, including the 26.4 GB weight blob. `MODEL_BYTE_PROOF` supplies
`manifest_sha256`, `weights_sha256`, `weights_bytes`, `all_manifest_blobs`, and
`verified_utc`; server version, installed digest/details and exact template are
checked before the first generation. Call order is fixed A/B for even context
indices and B/A for odd. The transport has an 18-call cap, records each attempt
before sending, flushes each result, and never retries. Output directories must be
fresh and outside the public repository.

Memory remains empty. [] is a projection of no observations, never an event.
No parser, Explorer, authority, decoding constraints, examples or composition
implementation changed. A separately approved research decision may consider
composition-v2; it was not implemented or run here.
