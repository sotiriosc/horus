"""Public-safe 30-decision review probe, then restore the 2048-token runner."""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import time
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from experiments.grounded_self_diagnosis_v0.protocol import (
    OPTIONS as HISTORICAL_REVIEW_OPTIONS, SYSTEM as HISTORICAL_REVIEW_SYSTEM,
    build_inputs,
)
from experiments.modern_memory_vs_horus_v0.storage import canonical

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("runtime_benchmark", HERE / "benchmark.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

def save(result):
    module.OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")

def main():
    result = json.loads(module.OUT.read_text())
    if result["status"] != "COMPLETE" or len(result["calls"]) != 11:
        raise RuntimeError("first-stage benchmark incomplete")
    if any(c["name"] == "B4_full_historical_review" for c in result["calls"]):
        raise RuntimeError("full review probe already recorded")
    full = build_inputs()["C"]
    prompt = canonical(full)
    options = dict(HISTORICAL_REVIEW_OPTIONS, num_predict=8, seed=54003)
    started = time.perf_counter()
    try:
        record = module.one("B4_full_historical_review", "B4", "30_decisions",
            prompt, HISTORICAL_REVIEW_SYSTEM, options=options, output_format=None)
        record["public_safe_input_sha256"] = hashlib.sha256(prompt.encode()).hexdigest()
        record["historical_review_runner_options"] = dict(num_ctx=8192,
            num_predict_original=1024, num_predict_benchmark=8)
        record["historical_source"] = "grounded_self_diagnosis_v0 public sanitized 30-decision input"
        result["calls"].append(record)
        save(result)
        print(json.dumps({k:record[k] for k in ("name","input_tokens","output_tokens",
            "load_duration_s","prompt_eval_duration_s","eval_duration_s",
            "wall_time_s","runner_pid")}), flush=True)
    except TimeoutError:
        record = dict(name="B4_full_historical_review", group="B4",
            prompt_shape="30_decisions", status="TIMEOUT_NO_RESPONSE",
            prompt_chars=len(prompt), input_tokens=None, output_tokens=None,
            wall_time_s=None, elapsed_at_least_s=round(time.perf_counter()-started, 3),
            load_duration_s=None, prompt_eval_duration_s=None, eval_duration_s=None,
            historical_context=8192, output_stored=False, world_executions=0,
            memory_writes=0, notes="No Ollama phase metadata; record as censored.")
        result["calls"].append(record)
        save(result)
        print(json.dumps({"name":record["name"], "status":record["status"],
            "elapsed_at_least_s":record["elapsed_at_least_s"]}), flush=True)
    finally:
        restored = module.one("B1_restore_ctx2048", "RESTORE", "tiny",
            module.CASES[0][3], "", options=module.OPTIONS, output_format="json")
        restored["purpose"] = "Restore original action runner context after full review probe"
        result["calls"].append(restored)
        result["historical_context_restored"] = bool(
            restored["runner_after"] and
            any(x.get("ctx_size") == 2048 for x in restored["runner_after"].values()))
        save(result)
        print(json.dumps({k:restored[k] for k in ("name","input_tokens",
            "load_duration_s","wall_time_s","runner_pid")}), flush=True)
    result["benchmark_model_calls_made"] = len(result["calls"])
    if any(x.get("status") == "TIMEOUT_NO_RESPONSE" for x in result["calls"]):
        result["status"] = "COMPLETE_WITH_CENSORED_FULL_REVIEW"
    save(result)

if __name__ == "__main__":
    main()
