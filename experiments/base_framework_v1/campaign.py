#!/usr/bin/env python3
"""Execute frozen v1 cross-source controls and external oracle audit."""

from __future__ import annotations

from dataclasses import replace
import hashlib
import json
from pathlib import Path
import tempfile
from typing import Optional

from experiments.base_framework_v1 import source_a, source_b
from experiments.base_framework_v1.framework import (
    CrossSourceFramework,
    EPISODE_LIMIT,
    MEMORY_LIMIT,
    StepResult,
    naive_pair_agreement,
)
from experiments.base_framework_v1.hidden_oracle import TrueTransition, TrueWorldOracle
from experiments.base_framework_v1.types import (
    DERIVED_SOURCE,
    OBSERVATION_B,
    SHARED_ANCESTOR,
    SHARED_OBSERVATION,
    SourceReceipt,
)


DRIVER_TRACE_LIMIT = 24


def retain_external_audit(
    trace: list[dict],
    event: TrueTransition,
    result: StepResult,
    rounds: list[tuple[SourceReceipt, Optional[SourceReceipt]]],
    false_accept: bool,
) -> None:
    if len(trace) >= DRIVER_TRACE_LIMIT:
        raise AssertionError("driver audit trace bound exceeded")
    final = rounds[-1] if rounds else (None, None)
    trace.append({
        "epoch": event.epoch,
        "transaction_id": event.transaction_id,
        "true_pre_state": event.pre_state,
        "action": event.action,
        "true_next_state": event.next_state,
        "true_consequence": event.consequence,
        "runtime_committed": result.committed,
        "runtime_continued": result.continued,
        "observation_rounds": len(rounds),
        "final_pair_structural": bool(
            final[0] and final[1] and independently_structural(final[0], final[1])
        ),
        "external_false_accept": false_accept,
    })


def independently_structural(a: SourceReceipt, b: SourceReceipt) -> bool:
    """Campaign-side recheck; deliberately does not call runtime authorizer."""

    return (
        a.source_id == "SOURCE_A"
        and b.source_id == "SOURCE_B"
        and a.fault_domain == "OBSERVATION_A"
        and b.fault_domain == "OBSERVATION_B"
        and a.lineage_class == "EXTERNAL_OBSERVATION"
        and b.lineage_class == "EXTERNAL_OBSERVATION"
        and a.observation_id != b.observation_id
        and (a.epoch, a.transaction_id, a.channel_sequence, a.pre_state, a.action)
        == (b.epoch, b.transaction_id, b.channel_sequence, b.pre_state, b.action)
        and a.observed_next_state == b.observed_next_state
        and a.observed_consequence == b.observed_consequence
    )


def audit_commit(system: CrossSourceFramework, event: TrueTransition, result: StepResult) -> bool:
    """Return true only when an authorized commit contradicts hidden truth."""

    if not result.committed:
        return False
    if not system.memory.records:
        return True
    record = system.memory.records[-1]
    return (
        record.epoch != event.epoch
        or record.transaction_id != event.transaction_id
        or record.pre_state != event.pre_state
        or record.action != event.action
        or record.next_state != event.next_state
        or record.consequence != event.consequence
        or system.map.current.state != event.next_state
    )


def make_receipts(
    system: CrossSourceFramework,
    event: TrueTransition,
    fault_a: Optional[str] = None,
    fault_b: Optional[str] = None,
    mode: Optional[str] = None,
) -> tuple[SourceReceipt, SourceReceipt]:
    request = system.observation_request(event.pre_state)
    a = source_a.observe(request, fault_a)
    b = source_b.observe(request, fault_b)
    if mode == "derived":
        b = replace(
            a,
            observation_id=a.observation_id | 0x80,
            source_id="SOURCE_B",
            fault_domain=OBSERVATION_B,
            lineage_class=DERIVED_SOURCE,
        )
    elif mode == "shared":
        a = replace(a, lineage_class=SHARED_ANCESTOR, fault_domain=SHARED_OBSERVATION)
        b = replace(b, lineage_class=SHARED_ANCESTOR, fault_domain=SHARED_OBSERVATION)
    return a, b


def drive(
    system: CrossSourceFramework,
    oracle: TrueWorldOracle,
    *,
    forced_action: Optional[str] = None,
    first_a: Optional[str] = None,
    first_b: Optional[str] = None,
    second_a: Optional[str] = None,
    second_b: Optional[str] = None,
    mode: Optional[str] = None,
    duplicate_a: bool = False,
    wrong_measure: bool = False,
    candidate_value: Optional[int] = None,
    failed_recovery: bool = False,
    wrong_memory_recovery: bool = False,
    delayed: bool = False,
) -> tuple[StepResult, TrueTransition, list[tuple[SourceReceipt, Optional[SourceReceipt]]]]:
    begun = system.begin_step(forced_action, wrong_memory_recovery)
    if isinstance(begun, StepResult):
        dummy = TrueTransition(system.epoch, begun.transaction_id, oracle.state, begun.action or "NONE", oracle.state, 0)
        return begun, dummy, []
    event = oracle.execute(begun.epoch, begun.transaction_id, begun.action)
    rounds: list[tuple[SourceReceipt, Optional[SourceReceipt]]] = []

    while True:
        reobserving = begun.reobservations > 0
        fault_a = second_a if reobserving else first_a
        fault_b = second_b if reobserving else first_b
        a, b = make_receipts(system, event, fault_a, fault_b, mode)
        partial = system.submit_receipt("A", a)
        if partial.committed:
            raise AssertionError("first source caused provisional commit")
        if delayed and not reobserving and partial.status.value != "OBSERVED_PARTIAL":
            raise AssertionError("delayed receipt did not remain partial")
        if duplicate_a:
            rounds.append((a, None))
            result = system.submit_receipt("A", a)
        else:
            rounds.append((a, b))
            result = system.submit_receipt(
                "B", b,
                wrong_measure=wrong_measure,
                candidate_value=candidate_value,
                failed_recovery=failed_recovery,
                common_mode=(mode == "common"),
            )
        system.assert_bounds()
        if not result.needs_reobservation:
            return result, event, rounds
        begun = system.pending
        if begun is None:
            raise AssertionError("re-observation requested without pending state")


def clean_episode(seed: int) -> tuple[dict, CrossSourceFramework]:
    system = CrossSourceFramework(0, seed)
    oracle = TrueWorldOracle(0)
    actions, pre_states = [], []
    audit_trace: list[dict] = []
    false_accepts = 0
    for _ in range(EPISODE_LIMIT):
        result, event, rounds = drive(system, oracle)
        if not result.committed or not result.continued:
            raise AssertionError("clean paired transaction failed")
        if len(rounds) != 1 or not independently_structural(*rounds[-1]):
            raise AssertionError("clean pair failed external structural audit")
        false_accept = audit_commit(system, event, result)
        false_accepts += false_accept
        retain_external_audit(audit_trace, event, result, rounds, false_accept)
        actions.append(result.action)
        pre_states.append(event.pre_state)
    state1 = [action for state, action in zip(pre_states, actions) if state == 1]
    if state1[0] != "ADVANCE" or "HOLD" not in state1[1:]:
        raise AssertionError("cross-source Memory did not change Explorer")
    if false_accepts:
        raise AssertionError("clean external false accept")
    if len(system.memory.records) != MEMORY_LIMIT or system.memory.evictions != 4:
        raise AssertionError("paired bounded rotation failed")
    system.metrics["memory_behavior_changes"] += 1
    system.metrics["clean_authorizations"] += EPISODE_LIMIT
    return ({
        "name": "clean_dual_source",
        "seed": seed,
        "status": "PASS",
        "result_class": "SAFE_AUTHORIZATION",
        "commits": EPISODE_LIMIT,
        "state1_actions": state1,
        "external_false_accepts": false_accepts,
        "driver_audit_records": audit_trace,
    }, system)


def scenario(name: str, seed: int) -> tuple[dict, CrossSourceFramework]:
    initial = 1 if name == "valid_incumbent" else 0
    system = CrossSourceFramework(initial, seed)
    oracle = TrueWorldOracle(initial)
    expected_commit = False
    result_class = "SAFE_REJECTION"
    naive_agreement = None

    if name == "a_transient":
        result, event, rounds = drive(system, oracle, first_a="wrong")
        expected_commit = True; result_class = "SUCCESSFUL_RECOVERY"
    elif name == "b_transient":
        result, event, rounds = drive(system, oracle, first_b="wrong")
        expected_commit = True; result_class = "SUCCESSFUL_RECOVERY"
    elif name == "a_persistent":
        result, event, rounds = drive(system, oracle, first_a="wrong", second_a="wrong")
    elif name == "b_persistent":
        result, event, rounds = drive(system, oracle, first_b="wrong", second_b="wrong")
    elif name == "stale_a":
        result, event, rounds = drive(system, oracle, first_a="stale")
        expected_commit = True; result_class = "SUCCESSFUL_RECOVERY"
    elif name == "stale_b":
        result, event, rounds = drive(system, oracle, first_b="stale")
        expected_commit = True; result_class = "SUCCESSFUL_RECOVERY"
    elif name == "wrong_epoch_a":
        result, event, rounds = drive(system, oracle, first_a="wrong_epoch", second_a="wrong_epoch")
    elif name == "wrong_epoch_b":
        result, event, rounds = drive(system, oracle, first_b="wrong_epoch", second_b="wrong_epoch")
    elif name == "wrong_transaction_a":
        result, event, rounds = drive(system, oracle, first_a="wrong_transaction", second_a="wrong_transaction")
    elif name == "wrong_transaction_b":
        result, event, rounds = drive(system, oracle, first_b="wrong_transaction", second_b="wrong_transaction")
    elif name == "delayed_second":
        result, event, rounds = drive(system, oracle, delayed=True)
        expected_commit = True; result_class = "SAFE_AUTHORIZATION"
    elif name == "duplicate_a":
        result, event, rounds = drive(system, oracle, duplicate_a=True)
    elif name == "source_spoof":
        result, event, rounds = drive(system, oracle, first_a="spoof_b", second_a="spoof_b")
    elif name == "derived_b":
        result, event, rounds = drive(system, oracle, mode="derived")
        naive_agreement = naive_pair_agreement(rounds[0][0], rounds[0][1])
    elif name == "shared_ancestor":
        result, event, rounds = drive(system, oracle, mode="shared")
        naive_agreement = naive_pair_agreement(rounds[0][0], rounds[0][1])
    elif name == "wrong_measure":
        result, event, rounds = drive(system, oracle, wrong_measure=True)
        expected_commit = True; result_class = "SUCCESSFUL_RECOVERY"
    elif name == "corrupted_memory":
        for _ in range(5):
            prior, prior_event, _ = drive(system, oracle)
            if audit_commit(system, prior_event, prior):
                raise AssertionError("setup false accept")
        system.memory.corrupt_consequence(2)
        result, event, rounds = drive(system, oracle)
        expected_commit = True; result_class = "SUCCESSFUL_RECOVERY"
    elif name == "invalid_recovery":
        result, event, rounds = drive(system, oracle, candidate_value=3, failed_recovery=True)
    elif name == "valid_incumbent":
        result, event, rounds = drive(system, oracle, forced_action="HOLD", candidate_value=2)
        expected_commit = True; result_class = "SAFE_AUTHORIZATION"
    elif name == "stale_incumbent":
        system.map.current.state = 3
        result, event, rounds = drive(system, oracle)
        expected_commit = True; result_class = "SUCCESSFUL_RECOVERY"
    elif name == "epoch_transition":
        prior, prior_event, _ = drive(system, oracle)
        if not prior.committed or audit_commit(system, prior_event, prior):
            raise AssertionError("epoch setup failed")
        system.start_epoch(seed + 100)
        result, event, rounds = drive(system, oracle)
        expected_commit = True; result_class = "SAFE_AUTHORIZATION"
    elif name == "common_mode":
        result, event, rounds = drive(system, oracle, first_a="wrong", first_b="wrong", mode="common")
        result_class = "OUT_OF_MODEL_COMMON_MODE_FAILURE" if audit_commit(system, event, result) else "SAFE_REJECTION"
    else:
        raise KeyError(name)

    external_false_accept = audit_commit(system, event, result)
    audit_trace: list[dict] = []
    retain_external_audit(audit_trace, event, result, rounds, external_false_accept)
    final_pair = rounds[-1] if rounds else (None, None)
    structural = bool(final_pair[0] and final_pair[1] and independently_structural(final_pair[0], final_pair[1]))
    if name == "common_mode":
        system.metrics["common_mode_false_accepts"] += int(external_false_accept)
        passed = (
            (result.committed and external_false_accept)
            or (not result.committed and not external_false_accept)
        )
    elif expected_commit:
        passed = result.committed and not external_false_accept
    else:
        passed = not result.committed and not result.continued and not external_false_accept
    if name in ("derived_b", "shared_ancestor"):
        passed = passed and naive_agreement is True and structural is False
    if name == "duplicate_a":
        passed = passed and all(pair[1] is None for pair in rounds)
    if name == "delayed_second":
        passed = passed and len(rounds) == 1
    if not passed:
        raise AssertionError(f"scenario failed: {name}: {result}")
    system.assert_bounds()
    return ({
        "name": name,
        "seed": seed,
        "status": "PASS",
        "result_class": result_class,
        "committed": result.committed,
        "continued": result.continued,
        "rounds": len(rounds),
        "external_false_accept": external_false_accept,
        "external_structural_final_pair": structural,
        "naive_agreement": naive_agreement,
        "metrics": dict(system.metrics),
        "driver_audit_records": audit_trace,
    }, system)


def execute_campaign() -> dict:
    names = (
        "a_transient", "b_transient", "a_persistent", "b_persistent",
        "stale_a", "stale_b", "wrong_epoch_a", "wrong_epoch_b",
        "wrong_transaction_a", "wrong_transaction_b", "delayed_second",
        "duplicate_a", "source_spoof", "derived_b", "shared_ancestor",
        "wrong_measure", "corrupted_memory", "invalid_recovery",
        "valid_incumbent", "stale_incumbent", "epoch_transition", "common_mode",
    )
    rows, systems = [], []
    for seed in (1, 2, 3):
        row, system = clean_episode(seed); rows.append(row); systems.append(system)
        for name in names:
            row, system = scenario(name, seed); rows.append(row); systems.append(system)

    totals = {key: sum(system.metrics[key] for system in systems) for key in systems[0].metrics}
    totals["scenario_runs"] = len(rows)
    totals["protected_false_accepts"] = sum(
        int(row.get("external_false_accept", row.get("external_false_accepts", 0)))
        for row in rows if row["name"] != "common_mode"
    )
    totals["externally_observed_false_rejects"] = sum(
        row["result_class"] in ("SAFE_AUTHORIZATION", "SUCCESSFUL_RECOVERY")
        and not row.get("committed", row.get("commits", 0) > 0)
        for row in rows
    )
    totals["max_memory_records"] = max(len(system.memory.records) for system in systems)
    totals["max_pair_decisions"] = max(len(system.pairs.decisions) for system in systems)
    totals["max_pending_receipts"] = max(system.max_pending_receipts for system in systems)
    totals["max_trace_records"] = max(system.max_trace for system in systems)
    totals["max_driver_audit_records"] = max(
        len(row["driver_audit_records"]) for row in rows
    )

    required = {
        "protected_false_accepts": 0,
        "externally_observed_false_rejects": 0,
        "duplicate_authorizations": 0,
        "memory_behavior_changes": 3,
    }
    for key, expected in required.items():
        if totals[key] != expected:
            raise AssertionError(f"frozen metric failed: {key}={totals[key]} expected {expected}")
    if totals["successful_reobservation_recoveries"] < 12:
        raise AssertionError("declared transient/stale recoveries did not complete")
    return {
        "status": "PASS",
        "claim": "SUPPORTED UNDER TESTED CONDITIONS: two structurally separate, provenance-matched observation channels gate bounded commit, transient disagreement re-observes once, persistent disagreement stops, and authorized history changes later behavior.",
        "parent_v0_commit": "6752f0adf591bf6ceacfe4b07cee967075f49c20",
        "seeds": [1, 2, 3],
        "bounds": {
            "world_states": 4, "actions": 3, "source_channels": 2,
            "receipts_per_round": 2, "observation_rounds": 2,
            "reobservation_attempts": 1, "pending_transactions": 1,
            "memory_records": 8, "pair_decisions": 8, "recovery_attempts": 1,
            "episode_transitions": 12, "epochs_per_scenario": 2,
            "trace_records": 24, "driver_audit_records": 24,
            "authorization_identities_per_epoch": 24,
        },
        "totals": totals,
        "scenarios": rows,
    }


def source_hashes(root: Path) -> dict[str, str]:
    directory = root / "experiments" / "base_framework_v1"
    return {
        str(path.relative_to(root)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(directory.glob("*.py"))
    }


def main() -> None:
    parser_output = None
    import argparse
    parser = argparse.ArgumentParser(); parser.add_argument("--output", type=Path)
    args = parser.parse_args(); parser_output = args.output
    root = Path(__file__).resolve().parents[2]
    output = parser_output or Path(tempfile.mkdtemp(prefix="horus-base-framework-v1-"))
    if parser_output:
        output.mkdir(parents=True, exist_ok=False)
    if output.resolve().is_relative_to(root):
        raise ValueError("evidence must remain outside source tree")
    result = execute_campaign(); result["source_sha256"] = source_hashes(root)
    (output / "results.json").write_text(json.dumps(result, indent=2) + "\n")
    print(
        "BASE FRAMEWORK V1 PASS: "
        f"scenarios={result['totals']['scenario_runs']}; "
        f"protected_false_accepts={result['totals']['protected_false_accepts']}; "
        f"false_rejects={result['totals']['externally_observed_false_rejects']}; "
        f"common_mode_false_accepts={result['totals']['common_mode_false_accepts']}; "
        f"evidence={output}"
    )


if __name__ == "__main__":
    main()
