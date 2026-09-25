"""String-only model transport and finite Explorer proposal adapter.

No framework mutation, evidence access, or authorization capability is passed
to the language model. The existing coordinator remains the action authority.
"""

from dataclasses import dataclass
import json
import urllib.request


ACTIONS = ("ADVANCE", "HOLD", "RETREAT")
SYSTEM = ("Choose exactly one allowed action. Prefer higher observed consequences. "
          "Reply only ADVANCE, HOLD, or RETREAT.")
OPTIONS = dict(temperature=0.2, top_p=0.9, top_k=40, num_predict=16,
               num_ctx=2048, repeat_penalty=1.1)
MODEL = "dolphin-mixtral:latest"


@dataclass(frozen=True)
class Coordinates:
    map_version: int
    epoch: int
    transaction_id: int


def visible_state(state, records, coordinates, with_memory=True, note=None):
    memory = [{key: getattr(r, key) for key in (
        "epoch", "transaction_id", "pre_state", "action", "next_state",
        "consequence", "pair_decision_id")}
        for r in records if r.pre_state == state] if with_memory else []
    payload = dict(state=state, map_version=coordinates.map_version,
                   epoch=coordinates.epoch, transaction_id=coordinates.transaction_id,
                   allowed_actions=list(ACTIONS), memory=memory)
    if note is not None:
        payload["non_authoritative_context"] = note
    return payload


def parse_action(raw):
    if not isinstance(raw, str):
        return None, "malformed"
    candidate = raw.strip()
    if candidate in ACTIONS:
        return candidate, None
    if candidate and candidate.replace("_", "").isalpha() and candidate.isupper():
        return None, "invalid_action"
    return None, "malformed"


class LocalModel:
    def __init__(self, endpoint="http://127.0.0.1:11434"):
        self.endpoint = endpoint

    def generate(self, prompt, seed):
        request = dict(model=MODEL, system=SYSTEM, prompt=prompt, stream=False,
                       options={**OPTIONS, "seed": seed})
        req = urllib.request.Request(self.endpoint + "/api/generate",
            data=json.dumps(request).encode(), headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=600) as response:
            result = json.load(response)
        if not result.get("done") or not isinstance(result.get("response"), str):
            raise RuntimeError("inference response incomplete")
        return result["response"], {key: result[key] for key in (
            "model", "created_at", "done", "total_duration", "load_duration",
            "prompt_eval_count", "prompt_eval_duration", "eval_count", "eval_duration") if key in result}


class ForcedOutput:
    """Explicit test injection, never represented as a real language-model call."""
    def __init__(self, raw):
        self.raw = raw

    def generate(self, prompt, seed):
        return self.raw, {"synthetic": True}


class ModelExplorerAdapter:
    def __init__(self, transport, coordinates, seed, with_memory=True, note=None):
        self.transport = transport
        self.coordinates = coordinates
        self.seed = seed
        self.with_memory = with_memory
        self.note = note
        self.observation = None

    def __deepcopy__(self, memo):
        # The frozen coordinator stages copies. This per-step I/O adapter holds
        # scalar metadata and its transcript only, never a framework reference.
        return self

    def choose(self, state, audited_records):
        payload = visible_state(state, audited_records, self.coordinates, self.with_memory, self.note)
        prompt = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        raw, metadata = self.transport.generate(prompt, self.seed)
        action, failure = parse_action(raw)
        self.observation = dict(model=MODEL, system=SYSTEM, input=payload,
            exact_prompt=prompt, options={**OPTIONS, "seed": self.seed},
            raw_output=raw, parsed_action=action, parse_failure=failure, response_metadata=metadata)
        # Only the existing framework gate can authorize this finite proposal.
        return action if action is not None else "INVALID_MODEL_PROPOSAL"
