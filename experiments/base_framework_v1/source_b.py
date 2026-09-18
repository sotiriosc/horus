"""Conditional observation channel B; imports no other source or oracle."""

from __future__ import annotations

from dataclasses import replace

from experiments.base_framework_v1.types import (
    EXTERNAL_OBSERVATION,
    OBSERVATION_B,
    ObservationRequest,
    SourceReceipt,
)


SOURCE_ID = "SOURCE_B"


def observe(request: ObservationRequest, fault: str | None = None) -> SourceReceipt:
    state = request.pre_state
    if request.action == "ADVANCE":
        next_state = (state + 1) & 3
        consequence = 1 if state % 2 == 0 else -1
    elif request.action == "HOLD":
        next_state = state
        consequence = 1 if state == 1 else 0
    elif request.action == "RETREAT":
        next_state = (state - 1) & 3
        consequence = -1 if state == 0 else (0 if state == 1 else 1)
    else:
        raise ValueError("Source B received unknown action")

    receipt = SourceReceipt(
        epoch=request.epoch,
        transaction_id=request.transaction_id,
        observation_id=(request.epoch << 24) | (request.transaction_id << 8) | 0x80 | request.channel_sequence,
        source_id=SOURCE_ID,
        channel_sequence=request.channel_sequence,
        pre_state=state,
        action=request.action,
        observed_next_state=next_state,
        observed_consequence=consequence,
        lineage_class=EXTERNAL_OBSERVATION,
        fault_domain=OBSERVATION_B,
    )
    if fault == "wrong":
        return replace(receipt, observed_next_state=(next_state + 1) & 3, observed_consequence=consequence + 7)
    if fault == "stale":
        return replace(receipt, channel_sequence=request.channel_sequence - 1)
    if fault == "wrong_epoch":
        return replace(receipt, epoch=request.epoch + 1)
    if fault == "wrong_transaction":
        return replace(receipt, transaction_id=request.transaction_id + 9)
    return receipt
