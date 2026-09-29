"""Read-only, public-safe engineering probe for the isolated Qwen3 server.

No protected world, receipt, authorization, or Memory component is imported.
Run from the repository root after starting the pinned llama-server.
"""
import hashlib
import importlib.util
import json
import subprocess
import sys
import time
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from experiments.modern_memory_vs_horus_v0.storage import canonical
from experiments.grounded_self_diagnosis_v0.protocol import build_inputs, SYSTEM as REVIEW_SYSTEM
from experiments.grounded_authority_autonomous_agent_v0.protocol import GOAL

AUDIT = ROOT / "engineering/grounded-agent-runtime-performance-v0"
spec = importlib.util.spec_from_file_location("frozen_benchmark", AUDIT / "benchmark.py")
frozen = importlib.util.module_from_spec(spec)
spec.loader.exec_module(frozen)
spec2 = importlib.util.spec_from_file_location("frozen_compact", AUDIT / "benchmark_compact.py")
compact = importlib.util.module_from_spec(spec2)
spec2.loader.exec_module(compact)

PORT = 18081
BASE = f"http://127.0.0.1:{PORT}"
ACTIONS = ("ADVANCE", "HOLD", "RETREAT")
ACTION_SCHEMA = {"type": "object", "properties": {"selected_action": {"type": "string", "enum": list(ACTIONS)}},
                 "required": ["selected_action"], "additionalProperties": False}


def sha(value):
    return hashlib.sha256(value.encode()).hexdigest()


def call(path, payload=None, timeout=180):
    body = None if payload is None else json.dumps(payload, separators=(",", ":")).encode()
    request = Request(BASE + path, data=body, headers={"Content-Type": "application/json"} if body else {})
    with urlopen(request, timeout=timeout) as response:
        return json.load(response)


def gpu():
    raw = subprocess.check_output(["nvidia-smi", "--query-gpu=memory.used,utilization.gpu",
                                   "--format=csv,noheader,nounits"], text=True).splitlines()[0]
    memory, utilization = (int(x.strip()) for x in raw.split(","))
    return {"memory_used_mib": memory, "utilization_pct": utilization}


def ask(name, system, prompt, allowed=ACTIONS, max_tokens=32, timeout=180, schema=True):
    schema_value = dict(ACTION_SCHEMA)
    schema_value["properties"] = {"selected_action": {"type": "string", "enum": list(allowed)}}
    request = {"messages": [{"role": "system", "content": system}, {"role": "user", "content": prompt}],
               "temperature": 0.2, "top_p": 0.9, "top_k": 40, "seed": 9071,
               "max_tokens": max_tokens, "stream": False, "cache_prompt": False,
               "chat_template_kwargs": {"enable_thinking": False}}
    if schema:
        request["response_format"] = {"type": "json_object", "schema": schema_value}
    before = gpu()
    started = time.perf_counter()
    response = call("/v1/chat/completions", request, timeout)
    wall = time.perf_counter() - started
    after = gpu()
    message = response["choices"][0]["message"]
    raw = message.get("content") or ""
    timings = response.get("timings", {})
    usage = response.get("usage", {})
    parsed = None
    if schema:
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            pass
    status = ("VALID" if isinstance(parsed, dict) and set(parsed) == {"selected_action"}
              and parsed["selected_action"] in allowed else "INVALID") if schema else "NOT_ACTION_OUTPUT"
    return {"name": name, "request_sha256": sha(json.dumps(request, sort_keys=True)),
            "prompt_sha256": sha(prompt), "prompt_characters": len(prompt), "system_characters": len(system),
            "allowed_actions": list(allowed) if schema else None,
            "input_tokens": usage.get("prompt_tokens"), "output_tokens": usage.get("completion_tokens"),
            "finish_reason": response["choices"][0].get("finish_reason"),
            "prompt_evaluated_tokens": timings.get("prompt_n"), "cache_reused_tokens": timings.get("cache_n"),
            "prompt_eval_duration_s": round(timings.get("prompt_ms", 0) / 1000, 4),
            "prompt_tokens_per_s": timings.get("prompt_per_second"),
            "generation_duration_s": round(timings.get("predicted_ms", 0) / 1000, 4),
            "generation_tokens_per_s": timings.get("predicted_per_second"),
            "wall_time_s": round(wall, 4), "gpu_before": before, "gpu_after": after,
            "cold_or_warm": "WARM_MODEL_ALREADY_LOADED", "model_load_duration_s_in_http_call": 0,
            "queue_duration_s": None,
            "raw_response": raw, "reasoning_content": message.get("reasoning_content"),
            "action_parse_status": status, "selected_action": parsed.get("selected_action") if status == "VALID" else None,
            "world_executions": 0, "memory_writes": 0}


def benchmarks():
    review_full = canonical(build_inputs()["C"])
    review_2000 = build_inputs()["C"]
    review_2000["completed_decisions"] = review_2000["completed_decisions"][:11]
    cases = [
        ("P1_tiny_first_final_pass", "", "State 0. HOLD established 0; ADVANCE unseen; RETREAT unseen. Allowed ADVANCE, HOLD, RETREAT. Choose one.", ACTIONS, 32, True),
        ("P1_tiny_warm", "", "State 0. HOLD established 0; ADVANCE unseen; RETREAT unseen. Allowed ADVANCE, HOLD, RETREAT. Choose one.", ACTIONS, 32, True),
        ("P2_compact", "", "Goal: maximize realized consequence. State: 0. ADVANCE UNSEEN; HOLD ESTABLISHED consequence 0; RETREAT UNSEEN. Allowed ADVANCE, HOLD, RETREAT. Unknown outcomes remain unknown. Authenticated grounded evidence is authoritative for established exact relations. Choose one allowed action.", ACTIONS, 32, True),
        ("P3_representative_action", frozen.ACTION_SYSTEM, frozen.representative(), ACTIONS, 32, True),
        ("P3_public_canonical_action", frozen.ACTION_SYSTEM, canonical(compact.public_projection()), ACTIONS, 32, True),
        ("P4_retrospective", frozen.REVIEW_SYSTEM, frozen.retrospective(), None, 128, False),
        ("P4_scaling_2000", REVIEW_SYSTEM, canonical(review_2000), None, 8, False),
        ("P5_full_public_review", REVIEW_SYSTEM, review_full, None, 256, False),
        ("G1_long_generation", "Answer concisely using only the supplied public-safe text.",
         "Write 150 distinct numbered observations about testing a local inference server; do not mention any world outcomes.", None, 192, False),
    ]
    result = {"status": "RUNNING", "server_port": PORT, "cache_prompt": False,
              "world_executions": 0, "memory_writes": 0, "cases": []}
    output = HERE / "benchmark-results.json"
    if output.exists():
        raise RuntimeError("refusing to overwrite completed benchmark; use a fresh output directory")
    for name, system, prompt, allowed, max_tokens, schema in cases:
        item = ask(name, system, prompt, allowed or ACTIONS, max_tokens,
                   240 if name.startswith("P5") else 180, schema)
        result["cases"].append(item)
        output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
        print(name, item["input_tokens"], item["output_tokens"], item["wall_time_s"], flush=True)
    result["status"] = "COMPLETE"
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")


def diagnostics():
    source = json.loads((ROOT / "research/grounded-action-sensitivity-v0/contexts.json").read_text())
    rows = []
    for name in ("A1", "A2", "B1", "B2", "C1", "C2"):
        fields = source["contexts"][name]
        assessments = {a: {k: v for k, v in fields["grounded_assessments"][a].items()
                            if k != "recent_receipt_provenance"} for a in ACTIONS}
        allowed = list(ACTIONS)
        if name == "B1":
            allowed.remove("ADVANCE")  # Explicit mechanical exclusion fixture.
        prompt = canonical({"goal": GOAL, "decision_index": 1, "current_state": 0,
                            "available_actions": allowed, "grounded_assessments": assessments,
                            "recent_agent_working_context": []})
        item = ask(name, frozen.ACTION_SYSTEM, prompt, allowed)
        item["grounded_kinds"] = {a: assessments[a]["kind"] for a in ACTIONS}
        item["expected_evidence_sensitive_action"] = {"A1":"ADVANCE","A2":"HOLD","B1":"HOLD",
                                                       "B2":"ADVANCE","C1":"HOLD","C2":"ADVANCE"}[name]
        rows.append(item)
    review = ask("R1_bounded_retrospective", REVIEW_SYSTEM, canonical(build_inputs()["C"]),
                 max_tokens=256, timeout=240, schema=False)
    if (HERE / "grounded-diagnostic-results.json").exists():
        raise RuntimeError("refusing to overwrite completed diagnostic; use a fresh output directory")
    output = {"status": "COMPLETE", "source": "public-safe frozen sensitivity contexts, with provenance stripped",
              "no_private_receipts_or_model_calls": True, "world_executions": 0, "memory_writes": 0,
              "sensitivity_pairs": [["A1", "A2"], ["B1", "B2"], ["C1", "C2"]],
              "decisions": rows, "retrospective": review}
    (HERE / "grounded-diagnostic-results.json").write_text(json.dumps(output, indent=2, sort_keys=True) + "\n")
    print("diagnostics", [(x["name"], x["selected_action"], x["action_parse_status"]) for x in rows], flush=True)


if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in ("benchmark", "diagnostic"):
        raise SystemExit("usage: python qualify.py benchmark|diagnostic")
    {"benchmark": benchmarks, "diagnostic": diagnostics}[sys.argv[1]]()
