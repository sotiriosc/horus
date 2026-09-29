# Blind diagnostic generalization v0

Prospective benchmark with **zero inference**. Twenty semantic worlds, six matched
pairs and four renderings each (80 future calls). Read [preregistration.md](preregistration.md)
for the frozen question, gates, limitations and mandatory stop-on-generator-bug rule.
No capability result exists until a separately authorized future campaign.

From the repository root, run deterministic development-seed tests:

```sh
python research/blind-diagnostic-generalization-v0/test_benchmark.py
```

Only after committing Method Freeze, materialize the final seed once:

```sh
python research/blind-diagnostic-generalization-v0/materialize.py --method-commit METHOD_SHA
```

The command requires HEAD to equal METHOD_SHA and every method file to match that
commit. It refuses to overwrite a materialization. A generator bug after this commit
requires stopping and a replacement preregistration, not repairing these files.

After materialization, verify without modifying any artifact:

```sh
python research/blind-diagnostic-generalization-v0/verify.py
```

`freeze-manifest.json` records Method Freeze and every materialized SHA-256.
`materialized/case-manifest.json`, `matched-pairs.json`, `render-manifest.json` and
`grading.json` are public grading artifacts, **not model input**. The only prospective
model payloads are `materialized/requests/*.json`; each contains a single generic
interface and allowlisted evidence, never gold or repository access. `worlds/` holds
canonical semantic evidence; `rendered/` holds the opaque case bodies. `verification.json`
records final regeneration, tests, preservation and non-execution checks.

A future transport implementation requires separate authorization. It must send only
the frozen requests in the frozen schedule, enforce model-runtime.json, isolate each
context and retain the raw first final string. Its private reasoning cannot be
passed to the scorer or published. Run verify.py successfully before dispatch and before scoring, and verify request
and output inventories against the frozen schedule. Any integrity breach is
INVALID_STUDY. The pure scoring API is:

```python
# Inputs loaded by a separately authorized host, not by the scorer itself.
protocol['matched_pairs'] = matched_pairs
result = score_benchmark(raw_final_strings_by_render_id, grading,
                         rendered_cases_by_render_id, schema, protocol,
                         violations=detected_protocol_violations)
```

No inference command/client is supplied here. The test suite's synthetic answers
are software fixtures only. Never submit them as observations or model results.
Python 3 with `jsonschema` is required; build environment versions are recorded in
`development-verification.json`. There are no external runtime dependencies for
world generation or rendering and no live Horus import/execution.
