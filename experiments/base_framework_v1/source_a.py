"""Table-driven observation channel A; imports no other source or oracle."""

from __future__ import annotations

from dataclasses import replace

from experiments.base_framework_v1.types import (
    EXTERNAL_OBSERVATION,
    OBSERVATION_A,
    ObservationRequest,
    SourceReceipt,
)


SOURCE_ID = "SOURCE_A"
_TABLE = {
    (0, "ADVANCE"): (1, 1), (0, "HOLD"): (0, 0), (0, "RETREAT"): (3, -1),
    (1, "ADVANCE"): (2, -1), (1, "HOLD"): (1, 1), (1, "RETREAT"): (0, 0),
    (2, "ADVANCE"): (3, 1), (2, "HOLD"): (2, 0), (2, "RETREAT"): (1, 1),
    (3, "ADVANCE"): (0, -1), (3, "HOLD"): (3, 0), (3, "RETREAT"): (2, 1),
}


def observe(request: ObservationRequest, fault: str | None = None) -> SourceReceipt:
    next_state, consequence = _TABLE[(request.pre_state, request.action)]
    receipt = SourceReceipt(
        request.epoch,
        request.transaction_id,
        (request.epoch << 24) | (request.transaction_id << 8) | request.channel_sequence,
        SOURCE_ID,
        request.channel_sequence,
        request.pre_state,
        request.action,
        next_state,
        consequence,
        EXTERNAL_OBSERVATION,
        OBSERVATION_A,
    )
    if fault == "wrong":
        return replace(receipt, observed_next_state=(next_state + 1) % 4, observed_consequence=consequence + 7)
    if fault == "stale":
        return replace(receipt, channel_sequence=request.channel_sequence - 1)
    if fault == "wrong_epoch":
        return replace(receipt, epoch=request.epoch + 1)
    if fault == "wrong_transaction":
        return replace(receipt, transaction_id=request.transaction_id + 9)
    if fault == "spoof_b":
        return replace(receipt, source_id="SOURCE_B")
    return receipt
