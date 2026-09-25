# Review snapshot verification

Executed 2026-09-25 against parent
`9219d313f3fca720c99bf7af9876d35e52ed89b9`, followed by an additive documentation
review. This records work performed for this handoff; it does not replace any
historical experiment report. Environment: Python 3.10.12, NumPy 2.2.6, GNU Make
4.3, Icarus Verilog 11.0. No live model inference occurred.

## Actual commands and results

Commands below use `$REVIEW` for the local evidence directory, with its
machine-specific prefix omitted. `PYTHONDONTWRITEBYTECODE=1` was set for test
processes. Logs and generated outputs are deliberately outside the public tree.

| Executed command | Actual result |
|---|---|
| `python -m experiments.grounded_lineage_rebaseline_v0.verify --repository . --output "$REVIEW/authority-and-mutation.json"` | PASS: 53 tests across eight existing suites plus 16 deterministic controls; zero model, network and legacy-law-authority calls. Contradictory receipt mutation retained both old and new evidence. |
| `python -m experiments.grounded_lineage_rebaseline_v0.dependencies --repository . --output "$REVIEW/dependencies"` | Exit 0; current dependency/legacy-import inventory regenerated. This is structural inventory, not an automatic claim-eligibility decision. |
| Six-module `python -m unittest` invocation below | PASS: 36 tests. |
| `python -m experiments.map_consequence_schema_transfer_v0.preflight --out "$REVIEW/latest-preflight"` | PASS: 16 canaries, eight matched request pairs, 16 detached-output variants, 11 J and 20 S parser rejections, 14 classification controls, seven category controls, per-world gate control, two durability controls; 16 synthetic responses and 16 byte-identical synthetic replay responses. 192 deterministic world executions; **zero actual model calls**. |
| `make test independent-commit independent-commit-followup` | PASS: core 53 executed steps; primary gate 21 schedules / 4,200 protected transactions and 300 expected negative-control false accepts; follow-up 2,700 broader-fault transactions and 21 paired trace comparisons. |
| Mechanical analyze/verify, twice, then byte comparisons below | Both runs exit 0; results and verification byte-identical between runs and to committed artifacts. 48 retained contexts, 6,912 exhaustive finite controls, 6,912 rebinding/order controls, 52 malformed forecasts and six invalid registrations; 153 manifest hash checks and 675 historical files preserved. |
| Forensic analyze/verify, twice, then byte comparisons below | Both runs exit 0; results and verification byte-identical between runs and to committed artifacts. 48 contexts, 144 forecasts, 180 history rows, 144 independent rankings and 685 historical files preserved. No model/world calls. |

The additional unit command was:

```bash
python -m unittest \
  experiments.cross_episode_stale_memory_feasibility_v0.test_fixture \
  experiments.model_map_proposal_v0.test_study \
  experiments.model_recovery_proposal_v1.test_study \
  experiments.model_proposal_role_composition_v2_replacement_r1.test_durability \
  experiments.explorer_value_aggregation_contract_v0.test_study \
  experiments.explorer_finite_value_comparator_v0.test_study
```

The retained-data repeatability check executed the following operations
(directory labels are normalized here):

```bash
for run in 1 2; do
  python -m experiments.mechanical_exploitation_baseline_v0.analyze --out "$REVIEW/mechanical-$run"
  python -m experiments.mechanical_exploitation_baseline_v0.verify --out "$REVIEW/mechanical-$run"
  python -m experiments.map_ranking_failure_forensics_v0.analyze --out "$REVIEW/forensics-$run"
  python -m experiments.map_ranking_failure_forensics_v0.verify --out "$REVIEW/forensics-$run"
done
for name in results verification; do
  cmp "$REVIEW/mechanical-1/$name.json" "$REVIEW/mechanical-2/$name.json"
  cmp "$REVIEW/mechanical-1/$name.json" "experiments/mechanical_exploitation_baseline_v0/$name.json"
  cmp "$REVIEW/forensics-1/$name.json" "$REVIEW/forensics-2/$name.json"
  cmp "$REVIEW/forensics-1/$name.json" "experiments/map_ranking_failure_forensics_v0/$name.json"
done
```

All eight comparisons passed. Mechanical output remains 25/48 versus 18/48,
19 ties and four wrong maxima. Forensics retains 23 residual positive
underpredictions, 116/144 consequence/latest matches, 111/144 exact joint
matches, and the 48/48 latest-value counterfactual, without an internal-cause
claim. Passing these checks does not upgrade the source's evidence category.

An additional isolated environment was created without system site packages:

```bash
python3 -m venv "$REVIEW/clean-venv"
"$REVIEW/clean-venv/bin/python" -m pip install -r requirements-test.txt numpy==2.2.6
PYTHONDONTWRITEBYTECODE=1 make test PYTHON="$REVIEW/clean-venv/bin/python"
```

Installation succeeded and the isolated core run passed all 53 executed steps.
This extra run checks setup reproducibility rather than new model behavior.

## Source, history and exclusions

The inspected source contains 754 tracked files (21,522,167 bytes), no submodules
or symlinks. Its reachable history has 144 commits and 866 unique blobs, no
merge commits, rooted at `8f7bee46ffe74d225de71d1ceeec6f29d3c41f60`. It is 130
commits ahead of public main `b8e4245ef14b11ee5d94ce851aec4d8dc059963f`.
No history is squashed or rewritten. The dedicated review commit adds only
`HORUS_STATE.md`, `REVIEW_GUIDE.md` and this file.

The full workspace inventory separated the public research lineage from dirty
private precursor source and separately retained evidence directories. None of
those private worktree changes, prompt documents, raw archives or precursor
history were imported. All public implementation, schemas, fixtures,
preregistrations, compact results and public RTL already present are retained.

Read-only scans of reachable blobs and commit objects checked likely credentials,
private keys, credential-bearing URLs, private home paths, predecessor markers,
binary/model weights and generated artifacts. No likely secrets or prohibited
private payloads were found. This is a heuristic content audit, not proof that
an arbitrary unknown secret cannot exist. The final staged diff is separately
reviewed before commit; no historical result, prompt, threshold or classification
is changed.

Four inherited JSONL files are intentionally public historical records: the
integration campaign's 69 calls, Memory study's 224 calls, and adaptive episode
study's 288 calls plus 288 steps. Their original public READMEs describe them.
The largest inherited text blob is the adaptive step file (4,570,029 bytes).
These are not newly exported private archives; their historical claim limits
still apply. Recent compact JSON also intentionally retains selected finite raw
response strings. Full private transport/journal/evidence archives stay excluded.

Other exclusions: local test logs and output directories, the fresh virtual
environment and downloaded dependencies, caches/build outputs, model weights
and Ollama blobs, personal files and machine-specific paths. No secret template
is required. Existing `.gitignore` bytes are preserved to keep frozen historical
manifests valid; generated handoff evidence is kept outside the tree.

## Reproducibility limits

The public mechanical/forensic finite-data results are reproducible as above.
The latest preflight validates public wiring, parsing, authority separation and
synthetic replay. It is not a new replay of the 16 real model responses from the
sealed transport archive. Full raw-source seals, request transport equality and
real-campaign replay require separately retained private evidence. No attempt
was made to reconstruct missing evidence or publish private archives.

No new inference, architecture development, Map redesign, prompt tuning,
threshold revision, hardware synthesis, Zakhor interaction or endurance study
was performed. This handoff does not claim testing every historical module.
Public main and existing tags are outside the review branch's publication scope.
