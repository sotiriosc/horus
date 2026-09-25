"""Trusted presentation bindings, not evidence or authorization components.

Callers supply framework-audited Memory. Transport receives only a prompt string
and seed. Parsers are imported unchanged. No model/server implementation lives here.
"""
from copy import deepcopy

from experiments.base_framework_v0.framework import Prediction
from experiments.model_explorer_semantic_prior_study_v0.adapter import parse_surface
from experiments.model_map_proposal_v0.adapter import parse as parse_prediction, serialize

ACTIONS = ('ADVANCE', 'HOLD', 'RETREAT')
FAMILIES = (('K1', 'K2', 'K3'), ('Q7', 'M4', 'Z2'))


def checked_mapping(mapping):
    if tuple(mapping) not in FAMILIES or set(mapping.values()) != set(ACTIONS):
        raise ValueError('complete registered opaque mapping required')
    return dict(mapping)


def checked_state(state):
    if type(state) is not int or state not in range(4):
        raise ValueError('finite current state required')


def history(state, action, records):
    """Projection only: authenticity is established by the existing caller audit."""
    return sorted((r for r in records if r.authorization == 'AUTHORIZED'
                   and r.pre_state == state and r.action == action),
                  key=lambda r: (r.epoch, r.transaction_id))


def explorer_payload(state, records, mapping):
    checked_state(state)
    mapping = checked_mapping(mapping)
    records = tuple(records)
    return dict(state=state, actions=[dict(action=token,
        verified_outcomes=[r.consequence for r in history(state, action, records)] or 'UNTRIED')
        for token, action in mapping.items()])


def map_payload(state, action, records, mapping):
    checked_state(state)
    mapping = checked_mapping(mapping)
    if action not in ACTIONS:
        raise ValueError('admitted finite action required')
    alias = next(token for token, value in mapping.items() if value == action)
    return dict(state=state, target_action=alias, VERIFIED_CHRONOLOGICAL_HISTORY=[
        dict(transaction_id=r.transaction_id, surface_action=alias,
             next_state=r.next_state, consequence=r.consequence)
        for r in history(state, action, records)])


class ExplorerBinding:
    def __init__(self, transport, mapping, seed):
        self.transport, self.mapping, self.seed = transport, checked_mapping(mapping), seed

    def __deepcopy__(self, memo):
        # Per-decision I/O binding owns no protected state or shadow Memory.
        return self

    def choose(self, state, audited_records):
        prompt = serialize(explorer_payload(state, audited_records, self.mapping))
        raw, _ = self.transport.generate(prompt, self.seed)
        _, action, _ = parse_surface(raw, dict(surface_option_order=list(self.mapping),
                                               surface_to_underlying=self.mapping))
        return action if action is not None else 'INVALID_MODEL_PROPOSAL'


class MapBinding:
    def __init__(self, base, memory, transport, mapping, seed):
        self.base, self.memory, self.transport = base, memory, transport
        self.mapping, self.seed = checked_mapping(mapping), seed

    def __deepcopy__(self, memo):
        clone = type(self)(deepcopy(self.base, memo), deepcopy(self.memory, memo),
                           self.transport, self.mapping, self.seed)
        memo[id(self)] = clone
        return clone

    @property
    def current(self): return self.base.current

    @property
    def quarantine(self): return self.base.quarantine

    def commit(self, value, epoch): self.base.commit(value, epoch)

    def quarantine_incumbent(self): self.base.quarantine_incumbent()

    def predict(self, action, epoch, transaction_id):
        # Existing coordinator calls this only AFTER parse/action admission and
        # its Memory audit. This reference follows the same staged Memory object.
        prompt = serialize(map_payload(self.current.state, action, self.memory.records, self.mapping))
        raw, _ = self.transport.generate(prompt, self.seed)
        value = parse_prediction(raw)
        return Prediction(epoch, transaction_id, self.current.state, action, **value)
