"""Finite Map proposal through the existing predict method; no event capability."""
from copy import deepcopy
import json
from experiments.base_framework_v0.framework import Prediction

SYSTEM = "Predict the next externally realized outcome for the specified action using only the verified chronological outcomes shown. Reply with exactly one JSON object containing next_state and consequence, and no explanation."
MODEL = "dolphin-mixtral:latest"
OPTIONS = dict(temperature=0.2, top_p=0.9, top_k=40, num_predict=32, num_ctx=2048, repeat_penalty=1.1)


def serialize(payload):
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def render(records, descriptor):
    alias = next(s for s,a in descriptor["mapping"].items() if a == "HOLD")
    return dict(state=1, target_action=alias, VERIFIED_CHRONOLOGICAL_HISTORY=[
        dict(transaction_id=r.transaction_id, surface_action=alias,
             next_state=r.next_state, consequence=r.consequence)
        for r in sorted(records, key=lambda r:(r.epoch,r.transaction_id))
        if r.authorization == "AUTHORIZED" and r.pre_state == 1 and r.action == "HOLD"])


def parse(raw):
    def unique(pairs):
        d = {}
        for k,v in pairs:
            if k in d: raise ValueError("duplicate field")
            d[k] = v
        return d
    if not isinstance(raw,str): raise ValueError("response is not text")
    value = json.loads(raw, object_pairs_hook=unique)
    if type(value) is not dict or set(value) != {"next_state","consequence"}:
        raise ValueError("exact prediction schema required")
    if any(type(v) is not int for v in value.values()): raise ValueError("exact integers required")
    if value["next_state"] not in range(4) or value["consequence"] not in (-1,0,1):
        raise ValueError("prediction outside finite domain")
    return value


class DeterministicExplorer:
    def choose(self, state, records):
        if state != 1: raise ValueError("registered target state required")
        return "HOLD"


class MapProposalAdapter:
    """Protected state is delegated; only predict receives the proposer output.

    The proposer receives immutable prompt text and a seed, never this adapter,
    the underlying Map, framework, receipt source, or an authorization callback.
    Staging copies protected state; the per-call proposer recorder is shared.
    """
    def __init__(self, base, proposer, prompt, seed):
        self.base, self.proposer, self.prompt, self.seed = base, proposer, prompt, seed

    def __deepcopy__(self, memo):
        clone = type(self)(deepcopy(self.base,memo), self.proposer, self.prompt, self.seed)
        memo[id(self)] = clone
        return clone

    @property
    def current(self): return self.base.current

    @property
    def quarantine(self): return self.base.quarantine

    def commit(self, value, epoch): self.base.commit(value,epoch)
    def quarantine_incumbent(self): self.base.quarantine_incumbent()

    def predict(self, action, epoch, transaction_id):
        if self.current.state != 1 or action != "HOLD": raise ValueError("outside registered Map target")
        raw = self.proposer(self.prompt,self.seed)
        value = parse(raw)
        return Prediction(epoch,transaction_id,self.current.state,action,**value)


INVALID = (
    "{", '{"next_state":1,"consequence":1} because',
    '{"next_state":4,"consequence":1}', '{"next_state":1,"consequence":2}',
    '{"next_state":true,"consequence":1}', '{"next_state":1.0,"consequence":1}',
    '{"next_state":1}', '{"next_state":1,"consequence":1,"extra":0}',
    '{"next_state":1,"consequence":1}{"next_state":1,"consequence":1}',
)
