# Composition input bindings v1

**A — COMPOSITION INPUT BINDINGS READY; zero model calls.** Two separate input
bindings generalize the finite Explorer/Map domains without editing historical
adapters, parsers or authority code. Historical composition-v0 remains blocked C.

Read the [37-section results](../../research/composition-input-bindings-v1-results.md),
[frozen preregistration](../../research/composition-input-bindings-v1-preregistration.md),
compact `results.json` and final `verification.json`. The campaign-level A requires
the replay/preservation/regression checks in verification before final completion.

From repository root, use fresh external directories:

```sh
python3 -m unittest experiments.composition_input_bindings_v1.test_bindings -v
python3 -m experiments.composition_input_bindings_v1.run --output "$HORUS_BINDINGS_CAMPAIGN"
python3 -m experiments.composition_input_bindings_v1.run --replay "$HORUS_BINDINGS_CAMPAIGN" --output "$HORUS_BINDINGS_REPLAY"
```

No server, model weights, network or inference is needed. The runner has no live
option. It retains full synthetic prompts/responses, transaction traces and summaries
outside the public tree. Replay uses the recorded synthetic responses and requires
all three evidence files byte-identical. Existing historical replay commands and
their evidence variables remain documented in the preceding experiment READMEs;
the actual 33-command run and old composition-v0 replay are listed in verification.

The new `ExplorerBinding` uses the original opaque parser. `MapBinding` uses the
original prediction parser and reads the same staged Memory object after existing
admission/audit. Their transports receive only prompt text and seed. Recovery uses
the unchanged Recovery v1 proposer. Registered synthetic expected contexts in these
fixtures do not constitute a general live transport implementation. Full authority
remains with the existing framework and external receipt boundary.

Do not launch the composed model campaign from this checkpoint automatically.
