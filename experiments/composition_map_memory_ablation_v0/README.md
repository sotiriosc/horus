# Composition Map Memory ablation v0

One prospectively frozen paired Map-only study: 42 preserved R1 contexts × authentic
history visible (H) / deliberately withheld (W), exactly 84 calls. No world execution,
Explorer, Recovery, new receipts, Memory writes or weight changes. Withheld does not
mean unknown. See the [preregistration](../../research/composition-map-memory-ablation-v0-preregistration.md)
and [42 frozen context identities](contexts.json).

Raw requests, responses, snapshots and preserved evaluator receipts remain in a
private persistent archive outside Git. Full local model bytes and the server
identity must match the pinned R1 runtime. The five preflight tests make no inference.
The request journal fsyncs intent, response and parsed result in order; an ambiguous
request stops without replacement. Live output and campaign reservations cannot be
reused automatically.

Zero-inference reproduction, with private retained source/response archives:

```sh
python3 -m experiments.composition_map_memory_ablation_v0.preflight --source "$R1_EVIDENCE" --output "$CHECKS/preflight.json"
python3 -m experiments.composition_map_memory_ablation_v0.run --source "$R1_EVIDENCE" --replay "$ABLATION_LIVE" --output "$ABLATION_REPLAY"
python3 -m experiments.composition_map_memory_ablation_v0.finalize --source "$R1_EVIDENCE" --live "$ABLATION_LIVE" --replay "$ABLATION_REPLAY" --assurance "$PRESERVATION_PROOF" --output "$FINAL_RESULTS"
```

The archived live command documents the authorized single campaign; it is **not**
authorization for another campaign:

```sh
python3 -m experiments.composition_map_memory_ablation_v0.preflight --source "$R1_EVIDENCE" --output "$CHECKS/preflight.json" --model-root "$OLLAMA_MODELS" --expected-model "$R1_MODEL_BYTE_PROOF"
python3 -m experiments.composition_map_memory_ablation_v0.run --live --source "$R1_EVIDENCE" --model-bytes "$CHECKS/model-bytes.json" --preflight "$CHECKS/preflight.json" --output "$ABLATION_LIVE"
```

Final results require exact reconstruction of eight registered files, including the
journal and raw metrics. Historical checks replay R1 and the schema study, run the
unchanged UNKNOWN tests and hash-preserve every inherited substantive file. No
unrelated live campaigns are rerun. Final scoring preserves the ten preregistered
conditions regardless of outcome. No push or automatic follow-up study.
