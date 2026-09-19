"""Action-only adapter; the transport receives strings and no authority objects."""

import json
import urllib.request

from experiments.model_explorer_integration_v0.adapter import MODEL, OPTIONS
from experiments.model_explorer_memory_study_v1.adapter import MemoryStudyAdapter, SYSTEM

SYSTEMS = {
    "A": SYSTEM,
    "B": SYSTEM + " When evidence is insufficient, you may choose an UNTRIED action to gather information.",
}


class AdaptiveAdapter(MemoryStudyAdapter):
    def __init__(self, *args, condition, **kwargs):
        super().__init__(*args, **kwargs, form="semantic")
        self.condition = condition

    def choose(self, state, audited_records):
        action = super().choose(state, audited_records)
        self.observation["system"] = SYSTEMS[self.condition]
        return action


class LocalModel:
    endpoint = "http://127.0.0.1:11434"

    def generate(self, prompt, seed, condition):
        request = urllib.request.Request(self.endpoint + "/api/generate",
            data=json.dumps(dict(model=MODEL, system=SYSTEMS[condition], prompt=prompt,
                stream=False, options={**OPTIONS, "seed": seed})).encode(),
            headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(request, timeout=600) as response:
            result = json.load(response)
        if not result.get("done") or not isinstance(result.get("response"), str):
            raise RuntimeError("incomplete inference response")
        return result["response"], {k: result[k] for k in (
            "model", "created_at", "done", "total_duration", "load_duration", "prompt_eval_count",
            "prompt_eval_duration", "eval_count", "eval_duration") if k in result}


class BoundTransport:
    def __init__(self, transport, condition):
        self.transport, self.condition = transport, condition

    def generate(self, prompt, seed):
        return self.transport.generate(prompt, seed, self.condition)
