# Reviewer guide

This branch preserves the complete public research tree at
`9219d313f3fca720c99bf7af9876d35e52ed89b9` and adds three review documents.
All 754 inherited files, including historical prompts and results, stay intact.
Use [HORUS_STATE.md](HORUS_STATE.md) for current scope; the root README retains
its original baseline scope because historical manifests pin its bytes.

## Reading order

1. [Current state](HORUS_STATE.md), especially the trust boundary and Map table.
2. [Clean-root manifest](experiments/grounded_lineage_rebaseline_v0/clean-root-manifest.json),
   [claim eligibility](experiments/grounded_lineage_rebaseline_v0/claim_eligibility.json),
   and [rebaseline report](research/grounded-lineage-rebaseline-v0-results.md).
3. [Status-bound authorizer](experiments/state_recovery_authorizer_status_binding_v1/framework.py),
   [grounded publication wrapper](experiments/realized_event_grounding_v0/framework.py),
   and [receipt boundary](experiments/realized_event_grounding_v0/receipt.py).
4. [Cross-role bindings](experiments/composition_input_bindings_v1/adapters.py),
   [cross-episode initialization](experiments/cross_episode_initialization_boundary_v1/boundary.py),
   and [authenticated projection](experiments/cross_episode_initialization_boundary_v1/projection.py).
5. [Mechanical chooser](experiments/mechanical_exploitation_baseline_v0/chooser.py),
   [its result](research/mechanical-exploitation-baseline-v0-results.md), then
   [ranking forensics](research/map-ranking-failure-forensics-v0-results.md).
6. The five recent Map diagnostics linked in the state table. For each, read
   `research/*-preregistration.md` before `research/*-results.md`; corresponding
   `experiments/*/` holds code, frozen inputs, schedule, compact results and
   reproduction instructions. In particular inspect the latest
   [preregistration](research/map-consequence-schema-transfer-v0-preregistration.md),
   [results](experiments/map_consequence_schema_transfer_v0/results.json) and
   [verification](experiments/map_consequence_schema_transfer_v0/verification.json).
7. The reproduction commands below and [actual handoff verification](review/VERIFICATION.md).
8. [Hardware mapping](docs/HARDWARE_FRAMEWORK_MAPPING.md),
   [bounded gate reproduction](experiments/bounded_commit/README.md), public
   `rtl/`, `tb/`, `sim/`, and [baseline reproduction](docs/REPRODUCIBILITY.md).

Especially inspect original-object receipt admission, preservation of the
pre-execution latch, independent recovery-status checks, late-failure atomicity,
retained contradictory observations, and detached-probe scoring. The three
consequence-only/schema diagnostic studies latch non-model control predictions
and publish receipt-derived outcomes. Successful control measurements are not
model accuracy.

## Clean checkout

Use a full clone: preservation checks inspect historical Git objects. Tested
with Python 3.10.12, NumPy 2.2.6, GNU Make 4.3 and Icarus Verilog 11.0 on Linux.
On Debian/Ubuntu, install system prerequisites if missing:

```bash
sudo apt-get install python3 python3-venv make iverilog
git clone --branch horus-review-current-state https://github.com/sotiriosc/horus.git
cd horus
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements-test.txt numpy==2.2.6
export PYTHONDONTWRITEBYTECODE=1
REVIEW=$(mktemp -d)
```

No secret configuration or `.env` is needed. Generated evidence stays outside
the checkout in `$REVIEW`. Keep that directory for your own verification; do
not commit it. The inherited `.gitignore` is preserved because it is also
hashed by historical frozen-input manifests.

## Current zero-inference verification

Run from repository root after setup. Output child directories must be new.

```bash
python -m experiments.grounded_lineage_rebaseline_v0.verify --repository . --output "$REVIEW/authority-and-mutation.json"
python -m experiments.grounded_lineage_rebaseline_v0.dependencies --repository . --output "$REVIEW/dependencies"
python -m unittest \
  experiments.cross_episode_stale_memory_feasibility_v0.test_fixture \
  experiments.model_map_proposal_v0.test_study \
  experiments.model_recovery_proposal_v1.test_study \
  experiments.model_proposal_role_composition_v2_replacement_r1.test_durability \
  experiments.explorer_value_aggregation_contract_v0.test_study \
  experiments.explorer_finite_value_comparator_v0.test_study
python -m experiments.map_consequence_schema_transfer_v0.preflight --out "$REVIEW/latest-preflight"
make test independent-commit independent-commit-followup
```

The grounded verifier runs eight existing suites and additional adversarial
controls with sockets/HTTP and legacy law-authority calls blocked. The latest
preflight uses **synthetic responses**, deterministic simulator executions and
synthetic replay; its printed `call` lines are not model inference. Neither
preflight nor successful fixture replay reruns the historical model campaign.

## Public retained-data reproduction of the Map bottleneck

These existing analyzers use public finite exports only. They do not execute
world actions or issue model calls. Reproduce and compare both output artifacts:

```bash
for study in mechanical_exploitation_baseline_v0 map_ranking_failure_forensics_v0; do
  python -m "experiments.$study.analyze" --out "$REVIEW/$study"
  python -m "experiments.$study.verify" --out "$REVIEW/$study"
  cmp "$REVIEW/$study/results.json" "experiments/$study/results.json"
  cmp "$REVIEW/$study/verification.json" "experiments/$study/verification.json"
done
```

Successful `cmp` is silent. Mechanical analysis recovers 25/48 versus 18/48,
19 ties and four wrong maxima. Forensics exposes all 23 residual positive
underpredictions and the 48/48 latest-value counterfactual. Both inherit the
source's synthetic/detached claim scope; neither proves a realized improvement.

Inspect the latest already-completed diagnostic without launching it:

```bash
python -m json.tool experiments/map_consequence_schema_transfer_v0/results.json
python - <<'PY'
import json
from pathlib import Path
studies = (
    "map_positive_evidence_depth_v0",
    "map_self_loop_consequence_coupling_v0",
    "map_consequence_only_isolation_v0",
    "map_output_schema_isolation_v0",
    "map_consequence_schema_transfer_v0",
)
for study in studies:
    data = json.loads((Path("experiments") / study / "results.json").read_text())
    print(study)
    for key in ("classification", "by_condition", "improvements", "regressions"):
        if key in data:
            print(key, json.dumps(data[key], sort_keys=True))
latest = json.loads(Path("experiments/map_consequence_schema_transfer_v0/results.json").read_text())
for call in latest["calls"]:
    d = call["descriptor"]
    print(call["index"] + 1, d["world"], d["family"], d["seed"],
          d["condition"], repr(call["raw_output"]), call["score"])
print("paired outcomes", json.dumps(latest["pairs"], sort_keys=True))
PY
```

This displays historical counts and records; it is not independent proof of
their acquisition. All 16 latest raw output strings are intentionally in the
compact public artifact. The full transport requests, journal and sealed
archive remain private. Full historical replay and original archive hash
verification require those retained archives, as each experiment README states.
The original in-process receipt identity cannot be recovered from public JSON.

**Live-inference commands are outside this review.** In particular,
`python -m experiments.map_consequence_schema_transfer_v0.run --live ...` would
launch a new campaign when supplied its required arguments. Other historical
`run` entrypoints have their own behavior; do not substitute them for the
explicit offline commands above. No model server, weights, credentials or
optional inference dependencies are required for this guide.

## Public scope

Earlier intentionally public model-call/step JSONL files remain historical
evidence, subject to the claim firewall. Later sealed raw archives and private
predecessor material are excluded. No private source was copied to complete the
hardware story. Test logs, generated data, dependencies and model weights are
not part of the branch. See the [audit record](review/VERIFICATION.md) for what
was scanned and what the scan can and cannot establish.
