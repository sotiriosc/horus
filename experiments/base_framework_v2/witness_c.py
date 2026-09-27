"""Independent low-bandwidth witness C; imports no source or oracle code."""

from __future__ import annotations

from dataclasses import replace

from experiments.base_framework_v1.types import ObservationRequest
from experiments.base_framework_v2.types import WitnessReceipt


WITNESS_ID = "WITNESS_C"
_ACTIONS = ("ADVANCE", "HOLD", "RETREAT")
# Flat independent representation of next_state * 3 + (consequence + 1).
_RELATION_CODES = (5, 1, 9, 6, 5, 1, 11, 7, 5, 0, 10, 8)


def encode_relation(next_state: int, consequence: int) -> int:
    return next_state * 3 + consequence + 1


def observe(
    request: ObservationRequest,
    registry_version: str,
    process_id: str = "WITNESS_PATH_C",
    fault: str | None = None,
) -> WitnessReceipt:
    index = request.pre_state * 3 + _ACTIONS.index(request.action)
    receipt = WitnessReceipt(
        request.epoch,
        request.transaction_id,
        (request.epoch << 24) | (request.transaction_id << 8) | 0x40 | request.channel_sequence,
        request.channel_sequence,
        process_id,
        registry_version,
        _RELATION_CODES[index],
    )
    if fault == "wrong":
        return replace(receipt, relation_code=(receipt.relation_code + 1) & 0xF)
    if fault == "stale_epoch":
        return replace(receipt, epoch=receipt.epoch - 1)
    if fault == "stale_transaction":
        return replace(receipt, transaction_id=receipt.transaction_id - 1)
    if fault == "spoof_process":
        return replace(receipt, process_id="UNKNOWN_PROCESS")
    return receipt
