"""Immutable data types shared by the two observation channels."""

from __future__ import annotations

from dataclasses import dataclass


EXTERNAL_OBSERVATION = "EXTERNAL_OBSERVATION"
DERIVED_SOURCE = "DERIVED_SOURCE"
SHARED_ANCESTOR = "SHARED_ANCESTOR"
OBSERVATION_A = "OBSERVATION_A"
OBSERVATION_B = "OBSERVATION_B"
SHARED_OBSERVATION = "SHARED_OBSERVATION"


@dataclass(frozen=True)
class ObservationRequest:
    epoch: int
    transaction_id: int
    pre_state: int
    action: str
    channel_sequence: int


@dataclass(frozen=True)
class SourceReceipt:
    epoch: int
    transaction_id: int
    observation_id: int
    source_id: str
    channel_sequence: int
    pre_state: int
    action: str
    observed_next_state: int
    observed_consequence: int
    lineage_class: str
    fault_domain: str
