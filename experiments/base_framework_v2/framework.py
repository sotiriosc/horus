"""V2 package gate around the unchanged v1 five-component loop."""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any

from experiments.base_framework_v1.framework import CrossSourceFramework, StepResult
from experiments.base_framework_v1.types import EXTERNAL_OBSERVATION, OBSERVATION_A, OBSERVATION_B
from experiments.base_framework_v2.registry import ProcessRegistry, normal_registry
from experiments.base_framework_v2.types import (
    AuthorizedPackage,
    RegisteredSourceEvidence,
    WitnessReceipt,
)
from experiments.base_framework_v2.witness_c import encode_relation


PACKAGE_LIMIT = 8
PACKAGE_ITEMS_PER_ROUND = 3
PACKAGE_TRACE_LIMIT = 24


@dataclass(frozen=True)
class PackageCheck:
    authorized: bool
    reason: str
    package: AuthorizedPackage | None = None


class EvidencePackageAuthorizer:
    """Sole validator for A+B+C structure, provenance, and relation agreement."""

    _EXPECTED = (
        ("source_a", "full_receipt"),
        ("source_b", "full_receipt"),
        ("witness", "relation_code"),
    )

    def authorize(
        self,
        pending: Any,
        a: object,
        b: object,
        c: object,
        registry: ProcessRegistry,
    ) -> PackageCheck:
        if isinstance(b, WitnessReceipt):
            return PackageCheck(False, "duplicate_witness")
        if not isinstance(a, RegisteredSourceEvidence) or not isinstance(b, RegisteredSourceEvidence):
            return PackageCheck(False, "evidence_type")
        if not isinstance(c, WitnessReceipt):
            return PackageCheck(False, "duplicate_witness")
        items = (a, b, c)
        process_ids = tuple(item.process_id for item in items)
        for item, (role, evidence_type) in zip(items, self._EXPECTED):
            node = registry.node(item.process_id)
            if node is None:
                return PackageCheck(False, "process_identity")
            if item.registry_version != registry.version:
                return PackageCheck(False, "registry_version")
            if node.allowed_role != role or node.evidence_type != evidence_type:
                return PackageCheck(False, "process_identity")
        if a.evidence_role != "source_a" or b.evidence_role != "source_b":
            return PackageCheck(False, "process_identity")
        expected = (pending.epoch, pending.transaction_id, pending.channel_sequence)
        for receipt in (a.receipt, b.receipt):
            if (receipt.epoch, receipt.transaction_id, receipt.channel_sequence) != expected:
                return PackageCheck(False, "stale_provenance")
            if receipt.action != pending.action:
                return PackageCheck(False, "stale_provenance")
        if (c.epoch, c.transaction_id, c.channel_sequence) != expected:
            return PackageCheck(False, "stale_provenance")
        if a.receipt.source_id != "SOURCE_A" or b.receipt.source_id != "SOURCE_B":
            return PackageCheck(False, "process_identity")
        if a.receipt.observation_id == b.receipt.observation_id:
            return PackageCheck(False, "process_identity")
        if (
            a.receipt.pre_state != b.receipt.pre_state
            or a.receipt.action != b.receipt.action
            or a.receipt.observed_next_state != b.receipt.observed_next_state
            or a.receipt.observed_consequence != b.receipt.observed_consequence
        ):
            return PackageCheck(False, "ab_disagreement")
        if c.relation_code != encode_relation(
            a.receipt.observed_next_state, a.receipt.observed_consequence
        ):
            return PackageCheck(False, "witness_disagreement")
        for index, left in enumerate(process_ids):
            for right in process_ids[index + 1 :]:
                if not registry.declared_separate(left, right):
                    reason = "candidate_derived" if c.process_id == "DERIVED_WITNESS" else "process_separation"
                    return PackageCheck(False, reason)
        package_id = (
            (pending.epoch << 40)
            | (pending.transaction_id << 16)
            | (pending.channel_sequence << 8)
            | 0xC3
        )
        return PackageCheck(True, "authorized_package", AuthorizedPackage(
            pending.epoch,
            pending.transaction_id,
            package_id,
            pending.channel_sequence,
            a.receipt.observation_id,
            b.receipt.observation_id,
            c.witness_id,
            process_ids,
            registry.version,
        ))


class EvidenceProvenanceFramework:
    def __init__(
        self,
        initial_state: int = 0,
        epoch: int = 1,
        registry: ProcessRegistry | None = None,
    ) -> None:
        self.inner = CrossSourceFramework(initial_state, epoch)
        self.registry = registry or normal_registry()
        self.package_authorizer = EvidencePackageAuthorizer()
        self.packages: list[AuthorizedPackage] = []
        self.staged: dict[str, object] = {}
        self.package_trace: list[tuple[int, int, str]] = []
        self.max_package_trace = 0
        self.max_staged_items = 0
        self.max_packages = 0
        self.metrics = {key: 0 for key in (
            "package_authorizations", "ab_disagreements", "witness_disagreements",
            "reobservations", "successful_transient_recoveries",
            "persistent_disagreement_rejections", "process_separation_rejections",
            "candidate_derived_rejections", "stale_provenance_rejections",
            "process_identity_rejections", "duplicate_witness_rejections",
            "ab_common_mode_attempts", "ab_common_mode_blocks",
            "abc_common_mode_false_accepts", "registry_corruption_false_accepts",
        )}

    def __getattr__(self, name: str) -> Any:
        return getattr(self.inner, name)

    def _trace(self, reason: str) -> None:
        pending = self.inner.pending
        identity = (pending.epoch, pending.transaction_id) if pending else (self.inner.epoch, 0)
        if len(self.package_trace) == PACKAGE_TRACE_LIMIT:
            self.package_trace.pop(0)
        self.package_trace.append((*identity, reason))
        self.max_package_trace = max(self.max_package_trace, len(self.package_trace))

    def _audit_package_ring(self) -> None:
        if len(self.packages) != len(self.inner.memory.records):
            raise RuntimeError("package/Memory ring length mismatch")
        for package, record in zip(self.packages, self.inner.memory.records):
            if (package.epoch, package.transaction_id) != (record.epoch, record.transaction_id):
                raise RuntimeError("package/Memory identity mismatch")

    def begin_step(self, **kwargs: Any) -> Any:
        self._audit_package_ring()
        self.staged.clear()
        return self.inner.begin_step(**kwargs)

    def start_epoch(self, epoch: int) -> None:
        self.inner.start_epoch(epoch)

    def observation_request(self, true_pre_state: int) -> Any:
        return self.inner.observation_request(true_pre_state)

    def stage(self, role: str, evidence: object) -> StepResult | None:
        if self.inner.pending is None:
            raise RuntimeError("no pending transaction")
        if role in self.staged:
            return self._fail_package("duplicate_witness" if role == "witness" else "process_identity")
        self.staged[role] = evidence
        self.max_staged_items = max(self.max_staged_items, len(self.staged))
        self._trace(f"staged_{role}")
        return None

    def submit_package(
        self,
        a: object,
        b: object,
        c: object,
        *,
        common_mode: bool = False,
        wrong_measure: bool = False,
        candidate_value: int | None = None,
        failed_recovery: bool = False,
    ) -> StepResult:
        if self.inner.pending is None:
            raise RuntimeError("no pending transaction")
        self.staged.clear()
        for role, evidence in (("source_a", a), ("source_b", b), ("witness", c)):
            early = self.stage(role, evidence)
            if early is not None:
                return early
        check = self.package_authorizer.authorize(
            self.inner.pending, self.staged["source_a"], self.staged["source_b"],
            self.staged["witness"], self.registry,
        )
        if not check.authorized:
            if common_mode:
                self.metrics["ab_common_mode_blocks"] += 1
            return self._fail_package(check.reason)
        assert check.package is not None
        self.metrics["package_authorizations"] += 1
        self._trace("PROCESS_VALIDATED")
        a_evidence = self.staged["source_a"]
        b_evidence = self.staged["source_b"]
        assert isinstance(a_evidence, RegisteredSourceEvidence)
        assert isinstance(b_evidence, RegisteredSourceEvidence)
        # The package registry is v2's provenance authority. Adapt its approved
        # port binding to the unchanged v1 interface instead of trusting the
        # candidate-carried v1 lineage/domain labels a second time.
        canonical_a = replace(
            a_evidence.receipt,
            lineage_class=EXTERNAL_OBSERVATION,
            fault_domain=OBSERVATION_A,
        )
        canonical_b = replace(
            b_evidence.receipt,
            lineage_class=EXTERNAL_OBSERVATION,
            fault_domain=OBSERVATION_B,
        )
        partial = self.inner.submit_receipt("A", canonical_a)
        if partial.committed:
            raise RuntimeError("commit occurred before complete package")
        oldest = self.packages[0] if len(self.packages) == PACKAGE_LIMIT else None
        result = self.inner.submit_receipt(
            "B", canonical_b, common_mode=common_mode,
            wrong_measure=wrong_measure, candidate_value=candidate_value,
            failed_recovery=failed_recovery,
        )
        if result.committed:
            if oldest is not None:
                self.packages.pop(0)
            self.packages.append(check.package)
            self.max_packages = max(self.max_packages, len(self.packages))
            self._audit_package_ring()
        self.staged.clear()
        return result

    def _fail_package(self, reason: str) -> StepResult:
        metric = {
            "ab_disagreement": "ab_disagreements",
            "witness_disagreement": "witness_disagreements",
            "process_separation": "process_separation_rejections",
            "candidate_derived": "candidate_derived_rejections",
            "stale_provenance": "stale_provenance_rejections",
            "process_identity": "process_identity_rejections",
            "registry_version": "process_identity_rejections",
            "evidence_type": "process_identity_rejections",
            "duplicate_witness": "duplicate_witness_rejections",
        }.get(reason, "process_identity_rejections")
        self.metrics[metric] += 1
        result = self.inner._dispute(reason)
        self.metrics["reobservations"] += int(result.needs_reobservation)
        if not result.needs_reobservation:
            self.metrics["persistent_disagreement_rejections"] += 1
        self._trace(reason)
        self.staged.clear()
        return result

    def assert_bounds(self) -> None:
        self.inner.assert_bounds()
        if len(self.registry.nodes) != 9:
            raise AssertionError("registry bound exceeded")
        if self.max_staged_items > PACKAGE_ITEMS_PER_ROUND:
            raise AssertionError("package item bound exceeded")
        if len(self.packages) > PACKAGE_LIMIT or self.max_packages > PACKAGE_LIMIT:
            raise AssertionError("package ring bound exceeded")
        if len(self.package_trace) > PACKAGE_TRACE_LIMIT:
            raise AssertionError("package trace bound exceeded")
