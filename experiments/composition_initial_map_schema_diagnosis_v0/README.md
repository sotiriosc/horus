# Composition initial Map schema diagnosis v0

**A — CONCRETE MODEL/PARSER SPECIFICATION GAP IDENTIFIED. Zero new model calls.**
All nine initial live Map objects return a string consequence despite the parser's
exact-integer requirement. Types/domains are not explicit in the model-visible
contract. Historical numeric examples and schema compliance differ, but this is
an association, not a causal explanation. Composition-v1 remains C.

Read the [21-section report](../../research/composition-initial-map-schema-diagnosis-v0-results.md),
[prospective protocol](../../research/composition-initial-map-schema-diagnosis-v0-preregistration.md),
compact `results.json` and `verification.json`.

From repository root, use the existing private archives and fresh external outputs:

```sh
python3 -m experiments.composition_initial_map_schema_diagnosis_v0.diagnose --composition "$COMPOSITION_EVIDENCE" --map0 "$MAP0_EVIDENCE" --map1 "$MAP1_EVIDENCE" --output "$DIAGNOSIS_OUTPUT"
python3 -m experiments.composition_initial_map_schema_diagnosis_v0.diagnose --composition "$COMPOSITION_EVIDENCE" --map0 "$MAP0_EVIDENCE" --map1 "$MAP1_EVIDENCE" --replay "$DIAGNOSIS_OUTPUT" --output "$DIAGNOSIS_REPLAY"
```

The input variables point to each study's retained `real` directory. No model/server,
weights or network is required. The diagnostic only reads archived text and calls
unchanged parsers/renderers. `diagnostic-private.json` retains exact raw strings,
request reconstruction, template text, field types/values, all historical classifications
and exact prompt diffs. Keep it private; public `results.json` contains compact
categories and representative field comparisons, not raw response transcripts.
Replay requires both generated files byte-identical.

Four focused original recorded-response replays (composition-v1, input-bindings-v1,
Map-v0, established-prior-v1) are documented in verification. All preceding source
hashes and branch/tag references were checked. No entire-history rerun, schema
change, response coercion, seeded Memory or new experiment was performed.
