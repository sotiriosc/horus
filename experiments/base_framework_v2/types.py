"""Immutable v2 evidence and authorization-package records."""

from __future__ import annotations

from dataclasses import dataclass

from experiments.base_framework_v1.types import SourceReceipt


@dataclass(frozen=True)
class RegisteredSourceEvidence:
    receipt: SourceReceipt
    process_id: str
    evidence_role: str
    registry_version: str


@dataclass(frozen=True)
class WitnessReceipt:
    epoch: int
    transaction_id: int
    witness_id: int
    channel_sequence: int
    process_id: str
    registry_version: str
    relation_code: int


@dataclass(frozen=True)
class AuthorizedPackage:
    epoch: int
    transaction_id: int
    package_id: int
    channel_sequence: int
    observation_a_id: int
    observation_b_id: int
    witness_id: int
    process_ids: tuple[str, str, str]
    registry_version: str
