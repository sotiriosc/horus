"""Benchmark-only exact public projection and compact rendering; no world decisions."""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import urllib.request

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from experiments.modern_memory_vs_horus_v0.storage import canonical
from experiments.grounded_authority_autonomous_agent_v0.protocol import GOAL, ACTION_SYSTEM
from experiments.grounded_self_diagnosis_v0.protocol import build_inputs, SYSTEM as REVIEW_SYSTEM

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("runtime_benchmark", HERE / "benchmark.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
PUBLIC = ROOT / "research/grounded-authority-autonomous-agent-v0/public-result.json"

def public_projection():
    data = json.loads(PUBLIC.read_text())
    if data["behavioral_campaign_status"] != "VALID":
        raise RuntimeError("public source campaign status differs")
    rows = data["runs"]["C"]["decisions"]
    d = rows[4]
    if d["decision_id"] != "C:D05" or d["state"] != 0:
        raise RuntimeError("public source decision differs")
    assessments = {a:{k:v for k,v in state.items() if k != "recent_receipt_provenance"}
        for a,state in d["grounded_assessments_before"].items()}
    history = [dict(decision_id=x["decision_id"], state=x["state"],
        action=x["selected_action"], authenticated_consequence=x["realized"]["consequence"],
        source=x["decision_source"]) for x in rows[1:4]]
    return dict(goal=GOAL, decision_id=d["decision_id"], decision_index=d["index"],
        current_state=d["state"], available_actions=d["admissible_actions"],
        grounded_assessments=assessments, recent_agent_working_context=history)

def compact(projection):
    lines = [
        "Goal: " + projection["goal"],
        f'Decision {projection["decision_id"]}; index {projection["decision_index"]}; state {projection["current_state"]}.',
        "Allowed: " + ", ".join(projection["available_actions"]) + ".",
        "Grounded assessments:",
    ]
    for action in ("ADVANCE", "HOLD", "RETREAT"):
        a = projection["grounded_assessments"][action]
        fields = [a["relation"], a["relation_type"], a["kind"],
            "status=" + a["assessment_status"], "observations=" + str(a["observation_count"])]
        if a["relation_type"] == "DETERMINISTIC":
            value = a["established_value"]
            established = "none" if value is None else f'next={value["next_state"]},consequence={value["consequence"]}'
            cand = a["candidate_value"]
            candidate = "none" if cand is None else json.dumps(cand,sort_keys=True,separators=(",",":"))
            fields += ["established=" + established, "candidate=" + candidate,
                "candidate_count=" + str(a["candidate_count"])]
        else:
            for key in ("segment_counts", "empirical_frequencies", "recent_window", "possible_change"):
                fields.append(key + "=" + json.dumps(a[key],sort_keys=True,separators=(",",":")))
        lines.append(action + ": " + "; ".join(fields) + ".")
    lines.append("Recent authenticated decision context:")
    for h in projection["recent_agent_working_context"]:
        lines.append(f'{h["decision_id"]}: state={h["state"]}, action={h["action"]}, '
            f'consequence={h["authenticated_consequence"]}, source={h["source"]}.')
    lines.append("Return only one selected_action from Allowed.")
    return "\n".join(lines)

def runner_port():
    for path in Path("/proc").iterdir():
        if not path.name.isdigit():
            continue
        try:
            args = (path / "cmdline").read_bytes().split(b"\0")
            if Path(args[0].decode()).name != "ollama-runner":
                continue
            text = [x.decode() for x in args if x]
            if text[text.index("--ctx-size") + 1] == "2048":
                return text[text.index("--port") + 1]
        except (OSError, ValueError, IndexError, UnicodeDecodeError):
            continue
    raise RuntimeError("no historical 2048-context runner available for tokenizer-only check")


def rendered(system, prompt):
    return "<|im_start|>system\n" + system + "<|im_end|>\n<|im_start|>user\n" + prompt + "<|im_end|>\n<|im_start|>assistant\n"


def token_count(port, system, prompt):
    req = urllib.request.Request("http://127.0.0.1:" + port + "/tokenize",
        data=json.dumps({"content": rendered(system, prompt)}).encode(),
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as response:
        return len(json.load(response)["tokens"])


def main():
    result = json.loads(module.OUT.read_text())
    if not result.get("historical_context_restored"):
        raise RuntimeError("historical action context not restored")
    projection = public_projection()
    exact_prompt = canonical(projection)
    compact_prompt = compact(projection)
    port = runner_port()
    counts = {
        "B3_public_canonical_rendered_tokens": token_count(port, ACTION_SYSTEM, exact_prompt),
        "C1_candidate_compact_rendered_tokens": token_count(port, ACTION_SYSTEM, compact_prompt),
        "B4_full_rendered_tokens": token_count(port, REVIEW_SYSTEM, canonical(build_inputs()["C"])),
        "B1_tiny_30_rendered_tokens": token_count(port, "", "Return {}."),
        "method": "Local runner /tokenize, without generation; four counts retained here.",
    }
    result["tokenizer_only_checks"] = counts
    result["compact_candidate_prompt_sha256"] = hashlib.sha256(compact_prompt.encode()).hexdigest()
    result["exact_public_projection_sha256"] = hashlib.sha256(exact_prompt.encode()).hexdigest()
    module.OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(counts, sort_keys=True))

if __name__ == "__main__":
    main()
