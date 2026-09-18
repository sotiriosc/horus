#!/usr/bin/env python3
"""Execute the frozen base framework v0 controls and failure campaign."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import tempfile

from experiments.base_framework_v0.environment import BoundedWorld
from experiments.base_framework_v0.framework import (
    AUTHORIZATION_RECORD_LIMIT,
    BaseFramework,
    EPOCH_LIMIT,
    EPISODE_LIMIT,
    MEMORY_LIMIT,
)


def checked_clean(seed: int) -> tuple[dict, BaseFramework]:
    world = BoundedWorld(0)
    system = BaseFramework(world, epoch=seed)
    actions = []
    pre_states = []
    for _ in range(EPISODE_LIMIT):
        result = system.run_step()
        if not result.committed or not result.continued:
            raise AssertionError("clean transaction did not commit")
        actions.append(result.action)
        pre_states.append(system.memory.records[-1].pre_state)
        system.assert_bounds()
        assert_authorized_history(system)

    state1_actions = [action for state, action in zip(pre_states, actions) if state == 1]
    if len(state1_actions) < 2 or state1_actions[0] != "ADVANCE" or "HOLD" not in state1_actions[1:]:
        raise AssertionError("Memory did not change later Explorer behavior")
    if len(system.memory.records) != MEMORY_LIMIT or len(system.evidence.receipts) != MEMORY_LIMIT:
        raise AssertionError("paired bounded rotation did not reach exact bound")
    valid, corrupt = system.memory.audit(system.evidence)
    if corrupt or len(valid) != MEMORY_LIMIT:
        raise AssertionError("bounded rotation corrupted identity")
    return ({
        "name": "clean_episode",
        "seed": seed,
        "status": "PASS",
        "transactions": EPISODE_LIMIT,
        "state1_actions": state1_actions,
        "memory_changed_future_behavior": True,
        "memory_records": len(system.memory.records),
        "evictions": system.memory.evictions,
        "incumbents_retained": system.metrics["incumbents_retained"],
        "candidate_replacements": system.metrics["candidate_replacements"],
    }, system)


def count_protected_false_accepts(system: BaseFramework) -> int:
    """Recheck committed records against the separate protected receipt ring."""

    count = 0
    for record in system.memory.records:
        receipt = system.evidence.find(
            record.epoch, record.transaction_id, record.observation_id
        )
        if not system.memory.record_matches_receipt(record, receipt):
            count += 1
    return count


def assert_authorized_history(system: BaseFramework) -> None:
    if count_protected_false_accepts(system):
        raise AssertionError("committed history failed protected-evidence recheck")
    memory_keys = [
        (record.epoch, record.transaction_id, record.observation_id)
        for record in system.memory.records
    ]
    if len(memory_keys) != len(set(memory_keys)):
        raise AssertionError("duplicate committed transaction identity")
    authorization_transactions = list(system.state_authorizer.authorized_keys)
    if len(authorization_transactions) != len(set(authorization_transactions)):
        raise AssertionError("duplicate state authorization for a transaction")


def run_scenario(name: str, seed: int) -> tuple[dict, BaseFramework]:
    initial_state = 1 if name == "valid_incumbent_over_bad_candidate" else 0
    world = BoundedWorld(initial_state)
    system = BaseFramework(world, epoch=seed)

    if name == "wrong_map_state":
        system.map.current.state = 2
        result = system.run_step()
        passed = result.committed and system.metrics["incumbents_quarantined"] == 1
        detail = "stale incumbent quarantined; protected pre-state recovery authorized"
    elif name == "corrupted_memory_record":
        for _ in range(5):
            system.run_step()
        system.memory.corrupt_consequence(2)
        result = system.run_step()
        passed = (
            result.committed
            and result.action == "HOLD"
            and system.metrics["memory_corruptions_detected"] == 1
            and not system.memory.quarantine
        )
        detail = "corrupt consequence detected before policy use and rebuilt from protected receipt"
    elif name == "wrong_measure_verdict":
        result = system.run_step({"wrong_measure": True})
        passed = result.committed and system.metrics["measurement_corruptions_detected"] == 1
        detail = "separate evidence auditor rejected verdict; corrected verdict authorized"
    elif name == "invalid_explorer_proposal":
        result = system.run_step({"forced_action": "JUMP"})
        passed = not result.executed and not result.committed and world.execution_count == 0
        detail = "invalid action rejected before environment execution"
    elif name == "failed_recovery":
        result = system.run_step({"candidate_value": 3, "failed_recovery": True})
        passed = not result.committed and not result.continued and system.metrics["recovery_rejections"] == 1
        detail = "invalid recovery rejected; invalid incumbent unavailable as fallback"
    elif name == "wrong_transaction":
        result = system.run_step({"candidate_transaction": 99})
        passed = result.committed and system.metrics["provenance_rejections"] == 1
        detail = "mismatched candidate rejected; fresh recovery independently authorized"
    elif name == "wrong_epoch":
        result = system.run_step({"candidate_epoch": seed + 1})
        passed = result.committed and system.metrics["provenance_rejections"] == 1
        detail = "stale/wrong epoch candidate rejected before fresh recovery"
    elif name == "shared_descendant":
        result = system.run_step({"shared_descendant": True})
        passed = (
            not result.committed
            and system.metrics["descendant_false_confidence"] == 1
            and system.metrics["lineage_rejections"] == 1
        )
        detail = "naive correlated checker agreed; protected authority rejected lineage"
    elif name == "stale_incumbent":
        system.map.current.state = 3
        result = system.run_step()
        passed = result.committed and system.metrics["incumbents_quarantined"] == 1
        detail = "verified-invalid incumbent quarantined rather than retained"
    elif name == "valid_incumbent_over_bad_candidate":
        result = system.run_step({"forced_action": "HOLD", "candidate_value": 2})
        passed = result.committed and result.incumbent_retained and system.map.current.state == 1
        detail = "valid incumbent retained when newer candidate failed evidence check"
    elif name == "unrecoverable_fault":
        result = system.run_step({"candidate_value": 2, "failed_recovery": True})
        passed = not result.committed and not result.continued
        detail = "unrecoverable transaction safely rejected with no history commit"
    elif name == "epoch_transition":
        first = system.run_step()
        system.start_epoch(seed + 100)
        result = system.run_step({"candidate_epoch": seed})
        passed = first.committed and result.committed and system.metrics["provenance_rejections"] == 1
        detail = "old-epoch candidate rejected; fresh-epoch recovery and commit succeeded"
    elif name == "wrong_memory_recovery":
        for _ in range(3):
            system.run_step()
        system.memory.corrupt_consequence(2)
        result = system.run_step({"wrong_memory_recovery": True})
        passed = not result.committed and system.metrics["recovery_rejections"] == 1
        detail = "invalid record recovery rejected without policy continuation"
    else:
        raise KeyError(name)

    system.assert_bounds()
    assert_authorized_history(system)
    if not passed:
        raise AssertionError(f"scenario failed: {name}: {result}")
    return ({
        "name": name,
        "seed": seed,
        "status": "PASS",
        "committed": result.committed,
        "continued": result.continued,
        "detail": detail,
        "metrics": dict(system.metrics),
    }, system)


def execute_campaign() -> dict:
    seeds = (1, 2, 3)
    failure_names = (
        "wrong_map_state",
        "corrupted_memory_record",
        "wrong_measure_verdict",
        "invalid_explorer_proposal",
        "failed_recovery",
        "wrong_transaction",
        "wrong_epoch",
        "shared_descendant",
        "stale_incumbent",
        "valid_incumbent_over_bad_candidate",
        "unrecoverable_fault",
        "epoch_transition",
        "wrong_memory_recovery",
    )
    scenarios = []
    systems = []
    for seed in seeds:
        clean, clean_system = checked_clean(seed)
        scenarios.append(clean)
        systems.append(clean_system)
        for name in failure_names:
            row, system = run_scenario(name, seed)
            scenarios.append(row)
            systems.append(system)

    totals = {
        key: sum(system.metrics[key] for system in systems)
        for key in systems[0].metrics
    }
    totals["world_executions"] = sum(system.environment.execution_count for system in systems)
    totals["scenario_runs"] = len(scenarios)
    counter_false_accepts = totals.pop("false_accepts")
    independently_observed_false_accepts = sum(
        count_protected_false_accepts(system) for system in systems
    )
    totals["protected_false_accepts"] = independently_observed_false_accepts
    totals["internal_false_accept_counter"] = counter_false_accepts
    totals["false_rejects"] = totals["false_rejects"]
    totals["duplicate_authorizations"] = totals["duplicate_authorizations"]
    totals["memory_behavior_changes"] = sum(
        bool(row.get("memory_changed_future_behavior")) for row in scenarios
    )

    if totals["protected_false_accepts"] != 0:
        raise AssertionError("protected false accept")
    if totals["false_rejects"] != 0:
        raise AssertionError("false reject")
    if totals["duplicate_authorizations"] != 0:
        raise AssertionError("duplicate authorization")
    if totals["descendant_false_confidence"] != len(seeds):
        raise AssertionError("negative control did not demonstrate false confidence")
    if totals["memory_behavior_changes"] != len(seeds):
        raise AssertionError("Memory did not change behavior for every seed")

    return {
        "status": "PASS",
        "claim": "SUPPORTED UNDER TESTED CONDITIONS: a bounded five-component closed loop with protected evidence, separate recovery verification, explicit authority, and history-dependent behavior.",
        "seeds": list(seeds),
        "bounds": {
            "world_states": 4,
            "actions": 3,
            "memory_records": MEMORY_LIMIT,
            "protected_receipts": MEMORY_LIMIT,
            "quarantine_entries_per_subsystem": 1,
            "recovery_candidates": 1,
            "recovery_attempts": 1,
            "trace_records": 16,
            "episode_transitions": EPISODE_LIMIT,
            "epochs_per_scenario": EPOCH_LIMIT,
            "authorization_records_per_epoch": AUTHORIZATION_RECORD_LIMIT,
        },
        "totals": totals,
        "scenarios": scenarios,
    }


def source_hashes(root: Path) -> dict[str, str]:
    directory = root / "experiments" / "base_framework_v0"
    return {
        str(path.relative_to(root)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(directory.glob("*.py"))
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[2]
    output = args.output or Path(tempfile.mkdtemp(prefix="horus-base-framework-v0-"))
    if args.output:
        output.mkdir(parents=True, exist_ok=False)
    if output.resolve().is_relative_to(root):
        raise ValueError("campaign evidence must remain outside the source tree")
    result = execute_campaign()
    result["source_sha256"] = source_hashes(root)
    (output / "results.json").write_text(json.dumps(result, indent=2) + "\n")
    print(
        "BASE FRAMEWORK V0 PASS: "
        f"{result['totals']['scenario_runs']} scenario runs; "
        f"protected_false_accepts={result['totals']['protected_false_accepts']}; "
        f"false_rejects={result['totals']['false_rejects']}; "
        f"duplicate_authorizations={result['totals']['duplicate_authorizations']}; "
        f"descendant_false_confidence={result['totals']['descendant_false_confidence']}; "
        f"evidence={output}"
    )


if __name__ == "__main__":
    main()
