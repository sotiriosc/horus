# Realized-event grounding v0

A separate core repair of the preserved contradiction-revision preflight failure. It reuses the historical five-component loop without editing old code. Read the [frozen protocol](../../research/realized-event-grounding-v0-preregistration.md) and [results](../../research/realized-event-grounding-v0-results.md).

The external driver owns `ExternalExecutionBoundary`. Components receive only its immutable read port. Only after completed execution does that boundary place an immutable receipt in its single pending slot. Authenticity requires the exact pending object, not a matching numeric value. The trusted source identity names a source lifetime; event IDs are monotonically unique in that bounded lifetime. The driver releases the slot after resolution. No receipt can originate at proposal time. This is a single-threaded software trust boundary, not protection against arbitrary same-process mutation or a physically dishonest external source.

A/B are content adapters with **shared receipt ancestry**. The new identity gate replaces stationary C; it is not an independent physical observation. No voting or artificial process-separation labels. Prediction is retained separately in the authorized package. Measure and Recovery reuse frozen behavior on the newly grounded pair. Eight aligned Memory/pair/package slots preserve historical observations and receipt provenance; ordinary bounded eviction remains. The package ring holds the original receipt object, not a reconstructed expectation. The source itself retains only one pending event, and executes at most 24 events across the two bounded epochs. Failed publication discards the staged Map/Memory/pair/package state.

## Reproduce (standard-library Python; no network or model)

From the repository root, use new output directories outside the public tree:

```sh
python3 -m unittest experiments.realized_event_grounding_v0.test_grounding -v
python3 -m experiments.realized_event_grounding_v0.run --output "$HORUS_EVENT_EVIDENCE"
python3 -m experiments.realized_event_grounding_v0.run --replay "$HORUS_EVENT_EVIDENCE" --output "$HORUS_EVENT_REPLAY"
```

Set both variables to distinct, previously nonexistent directories. The campaign always executes the exact changed-HOLD repair first, then changed ADVANCE, stationary cases, adversarial cases, root failure, bounded rotation and deterministic Memory causality. `campaign.json` contains bounded detailed transaction/root/attack/publication evidence. `results.json` contains compact counts and hashes. Exact replay regenerates both byte-for-byte. All 23 historical frozen source hashes are checked before/after execution.

The six additional unit tests cover failed execution/immutability, legacy ingress bypass, Measure repair, Memory repair, retained pair/Memory corruption and a root swap during staging. Test injection has access to the external driver only to exercise rejection; production candidate components do not receive that capability.

The root-failure control intentionally permits a wrong actual-world acceptance when the trusted emitter lies. It is explicitly outside the protected scope. No claim about model contradiction revision follows: zero model inference is performed.

Historical regression commands and recorded results are in `verification.json` and the results report. Prior model replays use retained transcripts; Semantic v0 and Prior-factorial v1 require their separately retained private evidence directories, whose hashes are recorded in their public checkpoints. The new deterministic repair campaign needs no private inputs.
