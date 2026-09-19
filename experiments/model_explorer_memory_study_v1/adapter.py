"""Factual presentation of audited Memory at the existing Explorer boundary."""

from dataclasses import asdict
import json
import urllib.request

from experiments.model_explorer_integration_v0.adapter import (
    ACTIONS, MODEL, OPTIONS, ModelExplorerAdapter, parse_action, visible_state,
)

SYSTEM = ("Choose an action using verified prior outcomes. Higher observed consequences are preferable. "
          "UNTRIED means no verified observation; it does not mean consequence 0. "
          "Reply with exactly one allowed action and no explanation.")


def presentation(canonical, form):
    records = canonical["memory"]
    seen = {r["action"] for r in records}
    untried = [a for a in ACTIONS if a not in seen]
    if form == "raw":
        memory = {"records": records, "UNTRIED": untried}
    elif form == "semantic":
        memory = {"VERIFIED_PRIOR_OUTCOMES": [
            {"action": a, "observed_consequences": [r["consequence"] for r in records if r["action"] == a]}
            for a in ACTIONS if a in seen], "UNTRIED": untried}
    else:
        raise ValueError("unknown preregistered presentation")
    return {**canonical, "memory": memory}


class MemoryStudyAdapter(ModelExplorerAdapter):
    def __init__(self, transport, coordinates, seed, with_memory=True, note=None, *, form):
        super().__init__(transport, coordinates, seed, with_memory, note)
        self.form = form

    def choose(self, state, audited_records):
        records = list(audited_records)
        canonical = visible_state(state, records, self.coordinates, self.with_memory)
        shown = presentation(canonical, self.form)
        prompt = json.dumps(shown, sort_keys=True, separators=(",", ":"))
        raw, metadata = self.transport.generate(prompt, self.seed)
        action, failure = parse_action(raw)
        self.observation = dict(model=MODEL, system=SYSTEM, options={**OPTIONS, "seed": self.seed},
            input=canonical, model_visible_input=shown, exact_prompt=prompt, form=self.form,
            authorized_relevant_records=[asdict(r) for r in records if r.pre_state == state],
            raw_output=raw, parsed_action=action, parse_failure=failure, response_metadata=metadata)
        return action if action is not None else "INVALID_MODEL_PROPOSAL"


class LocalModel:
    endpoint = "http://127.0.0.1:11434"

    def generate(self, prompt, seed):
        body = dict(model=MODEL, system=SYSTEM, prompt=prompt, stream=False,
                    options={**OPTIONS, "seed": seed})
        request = urllib.request.Request(self.endpoint + "/api/generate",
            data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(request, timeout=600) as response:
            result = json.load(response)
        if not result.get("done") or not isinstance(result.get("response"), str):
            raise RuntimeError("incomplete inference response")
        return result["response"], {k: result[k] for k in (
            "model", "created_at", "done", "total_duration", "load_duration", "prompt_eval_count",
            "prompt_eval_duration", "eval_count", "eval_duration") if k in result}
