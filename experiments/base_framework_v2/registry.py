"""Small immutable registry for declared evidence-process dependencies."""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType


@dataclass(frozen=True)
class ProcessNode:
    process_id: str
    parents: tuple[str, ...]
    fault_domain: str
    evidence_type: str
    allowed_role: str


class ProcessRegistry:
    def __init__(self, version: str, nodes: tuple[ProcessNode, ...]) -> None:
        if len(nodes) != 9 or len({node.process_id for node in nodes}) != 9:
            raise ValueError("registry must contain exactly nine unique nodes")
        self.version = version
        self.nodes = nodes
        self._by_id = MappingProxyType({node.process_id: node for node in nodes})
        for node in nodes:
            if any(parent not in self._by_id for parent in node.parents):
                raise ValueError("registry contains unknown parent")

    def node(self, process_id: str) -> ProcessNode | None:
        return self._by_id.get(process_id)

    def path(self, process_id: str) -> tuple[ProcessNode, ...]:
        seen: dict[str, ProcessNode] = {}

        def visit(identifier: str) -> None:
            if identifier in seen:
                return
            node = self._by_id[identifier]
            seen[identifier] = node
            for parent in node.parents:
                visit(parent)

        visit(process_id)
        return tuple(seen.values())

    def declared_separate(self, left: str, right: str) -> bool:
        permitted_nodes = {"TRUE_WORLD"}
        permitted_domains = {"WORLD_ROOT"}
        left_path, right_path = self.path(left), self.path(right)
        left_ids = {node.process_id for node in left_path} - permitted_nodes
        right_ids = {node.process_id for node in right_path} - permitted_nodes
        left_domains = {node.fault_domain for node in left_path} - permitted_domains
        right_domains = {node.fault_domain for node in right_path} - permitted_domains
        return not (left_ids & right_ids or left_domains & right_domains)


def _nodes(*, corrupt: bool) -> tuple[ProcessNode, ...]:
    derived_b = ProcessNode(
        "DERIVED_B_REFERENCE",
        ("TRUE_WORLD",) if corrupt else ("OBSERVATION_PATH_A",),
        "DECLARED_B" if corrupt else "OBSERVATION_A",
        "full_receipt",
        "source_b",
    )
    derived_c = ProcessNode(
        "DERIVED_WITNESS",
        ("TRUE_WORLD",) if corrupt else ("OBSERVATION_PATH_A",),
        "DECLARED_C" if corrupt else "OBSERVATION_A",
        "relation_code",
        "witness",
    )
    return (
        ProcessNode("TRUE_WORLD", (), "WORLD_ROOT", "root", "none"),
        ProcessNode("OBSERVATION_PATH_A", ("TRUE_WORLD",), "OBSERVATION_A", "full_receipt", "source_a"),
        ProcessNode("OBSERVATION_PATH_B", ("TRUE_WORLD",), "OBSERVATION_B", "full_receipt", "source_b"),
        ProcessNode("WITNESS_PATH_C", ("TRUE_WORLD",), "WITNESS_C", "relation_code", "witness"),
        derived_b,
        ProcessNode("SHARED_SENSOR", ("TRUE_WORLD",), "SHARED_SENSOR", "dependency", "none"),
        ProcessNode("SHARED_PATH_A", ("SHARED_SENSOR",), "SHARED_SENSOR", "full_receipt", "source_a"),
        ProcessNode("SHARED_PATH_B", ("SHARED_SENSOR",), "SHARED_SENSOR", "full_receipt", "source_b"),
        derived_c,
    )


def normal_registry() -> ProcessRegistry:
    return ProcessRegistry("V2-NORMAL-1", _nodes(corrupt=False))


def corrupted_registry() -> ProcessRegistry:
    """Out-of-model trust-root control: false parent/domain declarations."""
    return ProcessRegistry("V2-CORRUPT-CONTROL-1", _nodes(corrupt=True))
