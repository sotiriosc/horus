"""Separate cross-epoch Map projection. Historical adapters remain unchanged."""
from experiments.composition_input_bindings_v1.adapters import (
    checked_state, checked_mapping, history, ACTIONS, explorer_payload, serialize)


def map_payload(state, action, records, mapping):
    checked_state(state);mapping=checked_mapping(mapping)
    if action not in ACTIONS:raise ValueError('admitted finite action required')
    alias=next(k for k,v in mapping.items() if v==action)
    return dict(state=state,target_action=alias,VERIFIED_CHRONOLOGICAL_HISTORY=[
        dict(epoch=r.epoch,transaction_id=r.transaction_id,surface_action=alias,
             next_state=r.next_state,consequence=r.consequence)
        for r in history(state,action,records)])
