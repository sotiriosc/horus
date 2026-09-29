"""Metadata-only local Ollama performance probe; no world or Memory imports."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import threading
import time
import urllib.request
from datetime import datetime, timezone

MODEL = "dolphin-mixtral:latest"
DIGEST = "4b33b01bf33672a36945cd5925ffc9e3997a5e4d3119c7d59150bee0d2a0214a"
URL = "http://127.0.0.1:11434"
OUT = Path(__file__).with_name("benchmark-results.json")
OPTIONS = dict(num_ctx=2048, num_predict=8, temperature=0.2, top_p=0.9,
               top_k=40, repeat_penalty=1.1, seed=9071)
ACTION_SYSTEM = (
    "You are a reasoning component in a bounded world. Authenticated grounded assessments "
    "are authoritative for exact experienced deterministic relations. The admissible actions "
    "have already excluded inferior known actions. Choose one admissible action using only "
    "the shown goal, state, assessments, and bounded history. Unseen relations are unknown; "
    "empirical patterns and unresolved changes are not deterministic facts. You may explore "
    "a genuinely uncertain relation or select the best known admissible fallback. "
    "Return only a JSON object with exactly one selected_action field and no explanation."
)
REVIEW_SYSTEM = (
    "Review only the five completed decisions and authenticated outcomes shown. This is "
    "observational and cannot change future actions, prompts, rules, Memory, or weights. "
    "Do not infer hidden regimes or unexecuted counterfactuals. Return a short JSON object."
)

def get_json(path, payload=None, timeout=900):
    data = None if payload is None else json.dumps(payload, separators=(",", ":")).encode()
    req = urllib.request.Request(URL + path, data=data,
        headers={"Content-Type": "application/json"} if data else {})
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return json.load(response)

def gpu_sample():
    try:
        raw = subprocess.check_output(["nvidia-smi", "--query-gpu=memory.used,utilization.gpu",
            "--format=csv,noheader,nounits"], text=True, timeout=3).strip().splitlines()[0]
        a, b = (int(x.strip()) for x in raw.split(","))
        return {"memory_used_mib": a, "gpu_utilization_pct": b}
    except (OSError, ValueError, subprocess.SubprocessError, IndexError):
        return None

def runner_pids():
    result = {}
    for p in Path("/proc").iterdir():
        if not p.name.isdigit():
            continue
        try:
            cmd = (p / "cmdline").read_bytes().replace(b"\0", b" ").decode("utf-8", "replace")
        except (OSError, PermissionError):
            continue
        if cmd and Path(cmd.split()[0]).name == "ollama-runner":
            result[p.name] = {
                "gpu_layers": next((int(cmd.split("--n-gpu-layers ")[1].split()[0])
                    for _ in [0] if "--n-gpu-layers " in cmd), None),
                "ctx_size": next((int(cmd.split("--ctx-size ")[1].split()[0])
                    for _ in [0] if "--ctx-size " in cmd), None),
            }
    return result

def views():
    def item(kind, value=None):
        return dict(relation_type="DETERMINISTIC", kind=kind,
            established_value=None if value is None else dict(next_state=0, consequence=value),
            observation_count=0 if value is None else 3, recent_realized_consequences=[] if value is None else [value],
            uncertainty_reason=None)
    return dict(ADVANCE=item("UNSEEN"), HOLD=item("ESTABLISHED", 0),
                RETREAT=item("UNSEEN"))

def representative():
    return json.dumps(dict(goal="Maximize useful realized consequence over the run using the evidence available to you.",
        decision_id="C:D04", decision_index=4, current_state=0,
        available_actions=["ADVANCE", "HOLD", "RETREAT"],
        grounded_assessments=views(),
        recent_agent_working_context=[dict(decision_id=f"C:D{i:02d}", state=0,
            selected_action="HOLD", reason="Established zero fallback while other relations remain unseen.",
            realized=dict(next_state=0, consequence=0)) for i in range(1, 4)]),
        sort_keys=True, separators=(",", ":"))

def retrospective():
    decisions = [dict(decision_id=f"C:D{i:02d}", world_state=0,
        grounded_before=views(), selected_action="HOLD",
        recorded_reason="A zero fallback is known; unseen relations remain uncertain.",
        relied_on="authenticated grounded assessment",
        receipt=dict(action="HOLD", pre_state=0, next_state=0,
            realized_consequence=0), grounded_change="ESTABLISHED zero")
        for i in range(1, 6)]
    return json.dumps(dict(task="Summarize observed reasoning errors without proposing policy changes.",
        recent_decisions=decisions, review_is_non_authoritative=True),
        sort_keys=True, separators=(",", ":"))

def synthetic(target):
    return "Read-only synthetic prompt-size probe. Return an empty JSON object. " + ("state " * max(1, target - 18))

CASES = [
    ("B1_tiny_cold", "B1", "tiny", "State 0. HOLD is established zero. ADVANCE unseen. RETREAT unseen. Return an empty JSON object.", ""),
    ("B1_tiny_warm", "B1", "tiny", "State 0. HOLD is established zero. ADVANCE unseen. RETREAT unseen. Return an empty JSON object.", ""),
    ("B2_compact", "B2", "compact", "Goal: maximize realized consequence. State: 0. ADVANCE: UNSEEN. HOLD: ESTABLISHED 0 from authenticated experience. RETREAT: UNSEEN. Allowed: ADVANCE, HOLD, RETREAT. Unknown outcomes remain unknown. An established plus one would take priority. Return an empty JSON object.", ""),
    ("B3_representative_action", "B3", "representative", representative(), ACTION_SYSTEM),
    ("B4_retrospective", "B4", "retrospective", retrospective(), REVIEW_SYSTEM),
] + [(f"S{n}", "SCALING", str(n), synthetic(n), "") for n in (50, 100, 250, 500, 1000, 1900)]

def one(name, group, shape, prompt, system, options=None, output_format="json"):
    request = dict(model=MODEL, prompt=prompt, system=system, stream=False,
        options=OPTIONS if options is None else options)
    if output_format is not None:
        request["format"] = output_format
    before = runner_pids()
    samples = []
    stop = threading.Event()
    def observe():
        while not stop.is_set():
            s = gpu_sample()
            if s:
                samples.append(s)
            stop.wait(.7)
    observer = threading.Thread(target=observe, daemon=True)
    observer.start()
    started = time.perf_counter()
    try:
        response = get_json("/api/generate", request)
    finally:
        stop.set()
        observer.join(timeout=3)
    wall = time.perf_counter() - started
    after = runner_pids()
    if not response.get("done"):
        raise RuntimeError("incomplete model response")
    ns = lambda key: response.get(key, 0) / 1e9
    pt, ot = response.get("prompt_eval_count"), response.get("eval_count")
    prompt_s, eval_s = ns("prompt_eval_duration"), ns("eval_duration")
    record = dict(name=name, group=group, prompt_shape=shape,
        request_sha256=hashlib.sha256(json.dumps(request,sort_keys=True).encode()).hexdigest(),
        prompt_chars=len(prompt), system_chars=len(system), input_tokens=pt,
        output_tokens=ot, cold_or_warm="cold" if ns("load_duration") >= 1 else "warm",
        load_duration_s=round(ns("load_duration"), 6),
        prompt_eval_duration_s=round(prompt_s, 6),
        eval_duration_s=round(eval_s, 6),
        total_duration_s=round(ns("total_duration"), 6),
        wall_time_s=round(wall, 6),
        unaccounted_wall_s=round(wall - ns("total_duration"), 6),
        prompt_tokens_per_s=round(pt/prompt_s, 3) if pt is not None and prompt_s > 0 else None,
        generation_tokens_per_s=round(ot/eval_s, 3) if ot is not None and eval_s > 0 else None,
        gpu_memory_used_mib_peak=max((s["memory_used_mib"] for s in samples),default=None),
        gpu_utilization_pct_mean=round(sum(s["gpu_utilization_pct"] for s in samples)/len(samples), 1) if samples else None,
        gpu_utilization_pct_peak=max((s["gpu_utilization_pct"] for s in samples),default=None),
        gpu_samples=len(samples), runner_before=before, runner_after=after,
        runner_pid=next(iter(after),None),
        output_stored=False, world_executions=0, memory_writes=0)
    return record

def main():
    tags = get_json("/api/tags")
    model = next((m for m in tags["models"] if m["name"] == MODEL), None)
    if model is None or model["digest"] != DIGEST:
        raise RuntimeError("historical model digest mismatch")
    if OUT.exists():
        raise RuntimeError("refusing to overwrite benchmark results")
    artifact = dict(status="RUNNING", started_utc=datetime.now(timezone.utc).isoformat(),
        model=MODEL, digest=DIGEST, server="local Ollama 0.1.16",
        stable_options=OPTIONS, no_world_or_memory=True,
        note="Input tokens include model template and system field; outputs capped at 8 tokens.",
        calls=[])
    for name, group, shape, prompt, system in CASES:
        record = one(name, group, shape, prompt, system)
        artifact["calls"].append(record)
        OUT.write_text(json.dumps(artifact, indent=2, sort_keys=True)+"\n")
        print(json.dumps({k:record[k] for k in ("name","input_tokens","output_tokens",
            "cold_or_warm","load_duration_s","prompt_eval_duration_s","eval_duration_s",
            "wall_time_s","runner_pid")}), flush=True)
    artifact["status"]="COMPLETE"
    artifact["finished_utc"]=datetime.now(timezone.utc).isoformat()
    OUT.write_text(json.dumps(artifact, indent=2, sort_keys=True)+"\n")

if __name__ == "__main__":
    main()
