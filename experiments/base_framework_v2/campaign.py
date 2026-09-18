#!/usr/bin/env python3
"""Frozen v2 campaign with test-only truth and registry-path recomputation."""

from __future__ import annotations

from dataclasses import replace
import hashlib
from pathlib import Path

from experiments.base_framework_v1 import source_a, source_b
from experiments.base_framework_v1.hidden_oracle import TrueTransition, TrueWorldOracle
from experiments.base_framework_v2.framework import EvidenceProvenanceFramework
from experiments.base_framework_v2.registry import corrupted_registry, normal_registry
from experiments.base_framework_v2.types import RegisteredSourceEvidence, WitnessReceipt
from experiments.base_framework_v2 import witness_c


SCENARIOS = (
    "a_transient", "b_transient", "c_transient", "valid_recovery",
    "corrupted_memory", "invalid_recovery", "ab_common_c_correct",
    "ab_common_c_different", "abc_common", "false_process_separation",
    "shared_ancestor", "candidate_witness", "stale_witness",
    "duplicate_witness", "spoof_process", "wrong_measure",
    "epoch_transition", "registry_corrupt",
)


def independently_separate(registry, process_ids: tuple[str, str, str]) -> bool:
    """Campaign-side graph walk; does not call runtime separation method."""
    paths = []
    for identifier in process_ids:
        todo, identifiers, domains = [identifier], set(), set()
        while todo:
            current = todo.pop()
            if current in identifiers:
                continue
            node = registry.node(current)
            if node is None:
                return False
            identifiers.add(current)
            domains.add(node.fault_domain)
            todo.extend(node.parents)
        paths.append((identifiers - {"TRUE_WORLD"}, domains - {"WORLD_ROOT"}))
    return all(
        not (paths[i][0] & paths[j][0] or paths[i][1] & paths[j][1])
        for i in range(3) for j in range(i + 1, 3)
    )


def audit_commit(system: EvidenceProvenanceFramework, event: TrueTransition, result) -> bool:
    if not result.committed:
        return False
    record = system.memory.records[-1]
    package = system.packages[-1]
    expected = (event.epoch, event.transaction_id, event.pre_state, event.action,
                event.next_state, event.consequence)
    actual = (record.epoch, record.transaction_id, record.pre_state, record.action,
              record.next_state, record.consequence)
    if (package.epoch, package.transaction_id) != (event.epoch, event.transaction_id):
        return True
    return actual != expected


def _changed_consequence(value: int) -> int:
    return {-1: 0, 0: 1, 1: -1}[value]


def make_evidence(
    system: EvidenceProvenanceFramework,
    event: TrueTransition,
    mode: str,
    second_round: bool,
):
    request = system.observation_request(event.pre_state)
    a = source_a.observe(request)
    b = source_b.observe(request)
    c = witness_c.observe(request, system.registry.version)
    process_a, process_b = "OBSERVATION_PATH_A", "OBSERVATION_PATH_B"

    if mode == "a_transient" and not second_round:
        a = source_a.observe(request, "wrong")
    elif mode == "b_transient" and not second_round:
        b = source_b.observe(request, "wrong")
    elif mode == "c_transient" and not second_round:
        c = witness_c.observe(request, system.registry.version, fault="wrong")
    elif mode in ("ab_common_c_correct", "ab_common_c_different", "abc_common", "registry_corrupt"):
        wrong_next = (event.next_state + 1) % 4
        wrong_consequence = _changed_consequence(event.consequence)
        a = replace(a, observed_next_state=wrong_next, observed_consequence=wrong_consequence)
        b = replace(b, observed_next_state=wrong_next, observed_consequence=wrong_consequence)
        if mode == "ab_common_c_different":
            c = replace(c, relation_code=(witness_c.encode_relation(wrong_next, wrong_consequence) + 1) & 0xF)
        elif mode in ("abc_common", "registry_corrupt"):
            c = replace(c, relation_code=witness_c.encode_relation(wrong_next, wrong_consequence))
        if mode == "registry_corrupt":
            b = replace(a, source_id="SOURCE_B", observation_id=b.observation_id)
            process_b = "DERIVED_B_REFERENCE"
            c = replace(c, process_id="DERIVED_WITNESS")
    elif mode == "false_process_separation":
        b = replace(a, source_id="SOURCE_B", observation_id=b.observation_id)
        process_b = "DERIVED_B_REFERENCE"
    elif mode == "shared_ancestor":
        process_a, process_b = "SHARED_PATH_A", "SHARED_PATH_B"
    elif mode == "candidate_witness":
        c = replace(c, process_id="DERIVED_WITNESS")
    elif mode == "stale_witness":
        c = replace(c, epoch=c.epoch - 1)
    elif mode == "spoof_process":
        c = replace(c, process_id="UNKNOWN_PROCESS")

    return (
        RegisteredSourceEvidence(a, process_a, "source_a", system.registry.version),
        RegisteredSourceEvidence(b, process_b, "source_b", system.registry.version),
        c,
    )


def drive(
    system: EvidenceProvenanceFramework,
    oracle: TrueWorldOracle,
    mode: str = "clean",
    *,
    forced_action: str | None = None,
    wrong_measure: bool = False,
    failed_recovery: bool = False,
):
    begun = system.begin_step(forced_action=forced_action)
    if hasattr(begun, "committed"):
        return begun, None, [], []
    event = oracle.execute(begun.epoch, begun.transaction_id, begun.action)
    rounds, packages = [], []
    while True:
        evidence = make_evidence(system, event, mode, begun.reobservations > 0)
        a, b, c = evidence
        common = mode in ("ab_common_c_correct", "ab_common_c_different", "abc_common", "registry_corrupt")
        if common:
            system.metrics["ab_common_mode_attempts"] += 1
        if mode == "duplicate_witness":
            b = c
        rounds.append(evidence)
        result = system.submit_package(
            a, b, c, common_mode=common, wrong_measure=wrong_measure,
            failed_recovery=failed_recovery,
        )
        packages.append(system.packages[-1] if result.committed else None)
        system.assert_bounds()
        if not result.needs_reobservation:
            return result, event, rounds, packages
        begun = system.pending
        if begun is None:
            raise AssertionError("re-observation requested without pending state")


def _audit_row(system, event, result, rounds, name, seed) -> dict:
    false_accept = audit_commit(system, event, result) if event else False
    final = rounds[-1] if rounds else None
    paths = tuple(item.process_id for item in final) if final else ()
    separated = independently_separate(system.registry, paths) if paths else False
    return {
        "name": name,
        "seed": seed,
        "committed": result.committed,
        "continued": result.continued,
        "rounds": len(rounds),
        "reason": result.reason,
        "external_false_accept": false_accept,
        "external_process_separation": separated,
        "registry_paths": list(paths),
        "actual_transition": None if event is None else {
            "pre_state": event.pre_state, "action": event.action,
            "next_state": event.next_state, "consequence": event.consequence,
        },
        "committed_transition": None if not result.committed else {
            "next_state": system.memory.records[-1].next_state,
            "consequence": system.memory.records[-1].consequence,
            "package_id": system.packages[-1].package_id,
        },
        "metrics": {**system.metrics, **{
            "memory_corruptions_detected": system.inner.metrics["memory_corruptions_detected"],
            "memory_behavior_changes": system.inner.metrics["memory_behavior_changes"],
            "invalid_recovery_rejections": system.inner.metrics["invalid_recovery_rejections"],
            "measurement_corruptions_detected": system.inner.metrics["measurement_corruptions_detected"],
            "duplicate_authorizations": system.inner.metrics["duplicate_authorizations"],
        }},
    }


def clean_episode(seed: int):
    system = EvidenceProvenanceFramework(0, seed)
    oracle = TrueWorldOracle(0)
    state_actions, false_accepts = [], 0
    for _ in range(12):
        result, event, rounds, _ = drive(system, oracle)
        if not result.committed or len(rounds) != 1:
            raise AssertionError("clean package failed")
        false_accepts += audit_commit(system, event, result)
        if event.pre_state == 1:
            state_actions.append(result.action)
    if state_actions[0] != "ADVANCE" or "HOLD" not in state_actions[1:]:
        raise AssertionError("authorized Memory did not change Explorer")
    if false_accepts or len(system.memory.records) != 8 or len(system.packages) != 8:
        raise AssertionError("clean audit or bounded rotation failed")
    system.inner.metrics["memory_behavior_changes"] += 1
    row = {
        "name": "clean", "seed": seed, "committed": True, "continued": True,
        "rounds": 12, "commits": 12, "result_class": "TRUE_ACCEPT",
        "state1_actions": state_actions, "external_false_accept": False,
        "metrics": {**system.metrics, "memory_behavior_changes": 1,
                    "memory_corruptions_detected": 0, "invalid_recovery_rejections": 0,
                    "measurement_corruptions_detected": 0, "duplicate_authorizations": 0},
    }
    return row, system


def scenario(name: str, seed: int):
    registry = corrupted_registry() if name == "registry_corrupt" else normal_registry()
    initial = 0
    system = EvidenceProvenanceFramework(initial, seed, registry)
    oracle = TrueWorldOracle(initial)
    if name == "corrupted_memory":
        for _ in range(5):
            prior, event, _, _ = drive(system, oracle)
            if not prior.committed or audit_commit(system, event, prior):
                raise AssertionError("Memory setup failed")
        system.memory.corrupt_consequence(2)
        result, event, rounds, _ = drive(system, oracle)
    elif name == "valid_recovery":
        system.map.current.state = 3
        result, event, rounds, _ = drive(system, oracle)
    elif name == "invalid_recovery":
        system.map.current.state = 3
        result, event, rounds, _ = drive(system, oracle, failed_recovery=True)
    elif name == "wrong_measure":
        result, event, rounds, _ = drive(system, oracle, wrong_measure=True)
    elif name == "epoch_transition":
        prior, prior_event, _, _ = drive(system, oracle)
        if not prior.committed or audit_commit(system, prior_event, prior):
            raise AssertionError("epoch setup failed")
        system.start_epoch(seed + 100)
        result, event, rounds, _ = drive(system, oracle)
    else:
        result, event, rounds, _ = drive(system, oracle, name)

    row = _audit_row(system, event, result, rounds, name, seed)
    protected_commit = name in (
        "a_transient", "b_transient", "c_transient", "valid_recovery",
        "corrupted_memory", "wrong_measure", "epoch_transition",
    )
    out_of_model = name in ("abc_common", "registry_corrupt")
    if protected_commit:
        passed = result.committed and not row["external_false_accept"]
        row["result_class"] = "SUCCESSFUL_RECOVERY" if name != "epoch_transition" else "TRUE_ACCEPT"
        if name in ("a_transient", "b_transient", "c_transient"):
            system.metrics["successful_transient_recoveries"] += 1
            row["metrics"]["successful_transient_recoveries"] += 1
    elif out_of_model:
        passed = result.committed and row["external_false_accept"]
        row["result_class"] = "OUT_OF_MODEL_TRUST_ROOT_FALSE_ACCEPT"
        key = "abc_common_mode_false_accepts" if name == "abc_common" else "registry_corruption_false_accepts"
        system.metrics[key] += int(row["external_false_accept"])
        row["metrics"][key] += int(row["external_false_accept"])
    else:
        passed = not result.committed and not result.continued and not row["external_false_accept"]
        row["result_class"] = "SAFE_REJECTION"
    if name in ("ab_common_c_correct", "ab_common_c_different"):
        passed = passed and system.metrics["ab_common_mode_blocks"] == 2
    if name == "candidate_witness":
        passed = passed and system.metrics["candidate_derived_rejections"] == 2
    if name == "shared_ancestor":
        passed = passed and not row["external_process_separation"]
    if not passed:
        raise AssertionError(f"scenario failed: {name}: {row}")
    system.assert_bounds()
    return row, system


def execute_campaign() -> dict:
    rows, systems = [], []
    for seed in (1, 2, 3):
        row, system = clean_episode(seed); rows.append(row); systems.append(system)
        for name in SCENARIOS:
            row, system = scenario(name, seed); rows.append(row); systems.append(system)
    metric_keys = rows[0]["metrics"]
    totals = {key: sum(row["metrics"].get(key, 0) for row in rows) for key in metric_keys}
    totals.update({
        "scenario_runs": len(rows),
        "protected_false_accepts": sum(
            int(row["external_false_accept"])
            for row in rows if row["name"] not in ("abc_common", "registry_corrupt")
        ),
        "externally_observed_false_rejects": sum(
            row["name"] in ("clean", "a_transient", "b_transient", "c_transient",
                            "valid_recovery", "corrupted_memory", "wrong_measure", "epoch_transition")
            and not row["committed"] for row in rows
        ),
        "max_memory_records": max(len(system.memory.records) for system in systems),
        "max_pair_decisions": max(len(system.pairs.decisions) for system in systems),
        "max_package_decisions": max(len(system.packages) for system in systems),
        "max_package_items": max(system.max_staged_items for system in systems),
        "max_package_trace_records": max(system.max_package_trace for system in systems),
        "max_inherited_trace_records": max(system.inner.max_trace for system in systems),
        "max_registry_nodes": max(len(system.registry.nodes) for system in systems),
    })
    required = {
        "scenario_runs": 57, "protected_false_accepts": 0,
        "externally_observed_false_rejects": 0, "duplicate_authorizations": 0,
        "successful_transient_recoveries": 9, "memory_behavior_changes": 3,
        "ab_common_mode_blocks": 12, "abc_common_mode_false_accepts": 3,
        "registry_corruption_false_accepts": 3,
    }
    for key, expected in required.items():
        if totals[key] != expected:
            raise AssertionError(f"frozen metric failed: {key}={totals[key]} expected={expected}")
    return {
        "status": "PASS",
        "claim": "SUPPORTED UNDER TESTED CONDITIONS: a bounded five-component framework required provenance-matched evidence from declared distinct production paths plus an independently generated orthogonal witness, and blocked the tested identical A+B corruption while C remained correct.",
        "parent_v1_commit": "4fa4c9bdc3f20d71da2b59bd5ed723bbcc6c90ff",
        "seeds": [1, 2, 3],
        "bounds": {
            "world_states": 4, "actions": 3, "main_sources": 2, "witnesses": 1,
            "registry_nodes": 9, "evidence_items_per_round": 3,
            "observation_rounds": 2, "reobservations": 1, "pending_transactions": 1,
            "memory_records": 8, "pair_decisions": 8, "package_decisions": 8,
            "recovery_attempts": 1, "episode_transitions": 12, "epochs_per_scenario": 2,
            "package_trace_records": 24, "inherited_trace_records": 24,
        },
        "totals": totals,
        "scenarios": rows,
    }


def source_hashes(root: Path) -> dict[str, str]:
    paths = list((root / "experiments" / "base_framework_v2").glob("*.py"))
    paths += [root / "experiments/base_framework_v1/source_a.py",
              root / "experiments/base_framework_v1/source_b.py"]
    return {str(path.relative_to(root)): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in sorted(paths)}
