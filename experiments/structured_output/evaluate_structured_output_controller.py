#!/usr/bin/env python3
# SPDX-License-Identifier: CERN-OHL-S-2.0
"""
Reproducibility sweep for the structured-output consequence controller.

This is deliberately model-free: it tests whether the controller behavior is
stable across multiple prompts/candidates when checked against confirmed
ground-truth facts.  The language model's raw candidate is treated as input to
the controller, not as evidence that the task succeeded.
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments.structured_output.structured_output_controller import (  # noqa: E402
    JsonOutputContract,
    OperationBudget,
    deliver_structured_json,
)


RESULTS_PATH = ROOT / "results" / "structured_controller_reproducibility.json"


@dataclass(frozen=True)
class ControllerCase:
    case_id: str
    prompt: str
    contract: JsonOutputContract
    confirmed_facts: dict[str, Any] | None
    candidate: str
    expected_status: str
    finish_reason: str | None = None
    tokens_generated: int | None = None
    token_allowance: int | None = None
    budget_override: OperationBudget | None = None


def incident_contract() -> JsonOutputContract:
    return JsonOutputContract(
        required_keys=("summary", "incidents", "open_questions", "recommended_next_step"),
        field_types={
            "summary": str,
            "incidents": list,
            "open_questions": list,
            "recommended_next_step": str,
        },
        require_nonempty_strings=("summary", "recommended_next_step"),
    )


def order_contract() -> JsonOutputContract:
    return JsonOutputContract(
        required_keys=("item", "quantity"),
        field_types={"item": str, "quantity": int},
        require_nonempty_strings=("item",),
    )


def route_contract() -> JsonOutputContract:
    return JsonOutputContract(
        required_keys=("route_id", "priority", "requires_review"),
        field_types={"route_id": str, "priority": int, "requires_review": bool},
        require_nonempty_strings=("route_id",),
    )


def default_incident_facts() -> dict[str, Any]:
    return {
        "summary": "Telemetry validation incident requires strict JSON serialization.",
        "incidents": [
            {
                "subsystem": "telemetry",
                "severity": "medium",
                "detector": "schema_guard",
                "confidence": 0.91,
            }
        ],
        "open_questions": ["Which upstream service emitted the malformed payload?"],
        "recommended_next_step": "Quarantine the malformed candidate and serialize confirmed fields.",
    }


def build_cases() -> list[ControllerCase]:
    incident = incident_contract()
    return [
        ControllerCase(
            case_id="valid_incident_passthrough",
            prompt="Return the confirmed incident as strict JSON.",
            contract=incident,
            confirmed_facts=default_incident_facts(),
            candidate=json.dumps(default_incident_facts(), sort_keys=True),
            expected_status="ACCEPTED",
        ),
        ControllerCase(
            case_id="layer5_markdown_truncation",
            prompt="Return the confirmed incident as strict JSON.",
            contract=incident,
            confirmed_facts=default_incident_facts(),
            candidate="```json\n{",
            expected_status="RECOVERED",
            finish_reason="SHORT",
            tokens_generated=12,
            token_allowance=150,
        ),
        ControllerCase(
            case_id="schema_discussion_no_payload",
            prompt="Return item and quantity as strict JSON.",
            contract=order_contract(),
            confirmed_facts={"item": "apple", "quantity": 3},
            candidate="The JSON schema should contain an item string and a quantity integer.",
            expected_status="RECOVERED",
        ),
        ControllerCase(
            case_id="wrong_value_plus_extra_key",
            prompt="Return item and quantity as strict JSON.",
            contract=order_contract(),
            confirmed_facts={"item": "apple", "quantity": 3},
            candidate='{"item":"apple","quantity":99,"note":"model guessed"}',
            expected_status="RECOVERED",
        ),
        ControllerCase(
            case_id="type_mismatch_route",
            prompt="Return route decision as strict JSON.",
            contract=route_contract(),
            confirmed_facts={"route_id": "alpha-7", "priority": 2, "requires_review": True},
            candidate='{"route_id":"alpha-7","priority":"high","requires_review":"yes"}',
            expected_status="RECOVERED",
        ),
        ControllerCase(
            case_id="missing_ground_truth_halts",
            prompt="Return item and quantity as strict JSON.",
            contract=order_contract(),
            confirmed_facts={"item": "apple"},
            candidate='{"item":"apple","quantity":99}',
            expected_status="NEEDS_INPUT",
        ),
        ControllerCase(
            case_id="budget_guard_stops",
            prompt="Return item and quantity as strict JSON.",
            contract=order_contract(),
            confirmed_facts={"item": "apple", "quantity": 3},
            candidate="not json",
            expected_status="STOPPED",
            budget_override=OperationBudget(units=1, check_cost=1, recovery_cost=1, recovery_check_cost=1),
        ),
    ]


def default_budget(args: argparse.Namespace) -> OperationBudget:
    return OperationBudget(
        units=int(args.units),
        attempt_cost=int(args.attempt_cost),
        check_cost=int(args.check_cost),
        recovery_cost=int(args.recovery_cost),
        recovery_check_cost=int(args.recovery_check_cost),
        max_attempts=int(args.max_attempts),
    )


def final_matches_facts(status: str, output: str | None, facts: dict[str, Any] | None) -> bool:
    if status == "NEEDS_INPUT":
        return output is None
    if status == "STOPPED":
        return output is None
    if facts is None or output is None:
        return False
    try:
        parsed = json.loads(output)
    except json.JSONDecodeError:
        return False
    return parsed == {key: facts[key] for key in parsed.keys()} and parsed == facts


def print_table(rows: list[dict[str, Any]]) -> None:
    print("| Case | Expected | Status | Final Procedure | Exact Ground Truth | Revoked | Remaining Units | Insistence Denied |")
    print("|---|---|---|---|---:|---:|---:|---:|")
    for row in rows:
        print(
            "| {case} | {expected} | {status} | {procedure} | {exact} | {revoked} | {units} | {insist} |".format(
                case=row["case_id"],
                expected=row["expected_status"],
                status=row["status"],
                procedure=row["final_procedure"],
                exact="yes" if row["final_matches_ground_truth"] else "no",
                revoked="yes" if row["revoked_procedures"] else "no",
                units=row["remaining_units"],
                insist="yes" if row["insistence_denied"] else "n/a",
            )
        )


def run_case(case: ControllerCase, budget: OperationBudget) -> dict[str, Any]:
    selected_budget = case.budget_override or budget
    outcome = deliver_structured_json(
        candidate=case.candidate,
        confirmed_facts=case.confirmed_facts,
        contract=case.contract,
        budget=selected_budget,
        finish_reason=case.finish_reason,
        tokens_generated=case.tokens_generated,
        token_allowance=case.token_allowance,
    )
    payload = outcome.to_json()
    insistence = payload.get("adversarial_insistence_test")
    return {
        "case_id": case.case_id,
        "prompt": case.prompt,
        "candidate": case.candidate,
        "expected_status": case.expected_status,
        "status": payload["status"],
        "status_matches_expected": payload["status"] == case.expected_status,
        "final_procedure": payload["final_procedure"],
        "remaining_units": payload["remaining_units"],
        "revoked_procedures": payload["revoked_procedures"],
        "initial_failures": None if payload["initial_validation"] is None else payload["initial_validation"]["failures"],
        "final_matches_ground_truth": final_matches_facts(payload["status"], payload["output"], case.confirmed_facts),
        "insistence_denied": None if insistence is None else not bool(insistence["resume_allowed"]),
        "contract": case.contract.to_json(),
        "budget": selected_budget.to_json(),
        "outcome": payload,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--units", type=int, default=64)
    parser.add_argument("--attempt-cost", type=int, default=20)
    parser.add_argument("--check-cost", type=int, default=5)
    parser.add_argument("--recovery-cost", type=int, default=20)
    parser.add_argument("--recovery-check-cost", type=int, default=5)
    parser.add_argument("--max-attempts", type=int, default=1)
    parser.add_argument("--results", type=Path, default=RESULTS_PATH)
    parser.add_argument("--show-outputs", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    budget = default_budget(args)
    rows = [run_case(case, budget) for case in build_cases()]
    pass_count = sum(
        1
        for row in rows
        if row["status_matches_expected"] and row["final_matches_ground_truth"]
    )
    artifact = {
        "experiment": "STRUCTURED_CONTROLLER_REPRODUCIBILITY",
        "default_budget": budget.to_json(),
        "total_cases": len(rows),
        "passed_cases": pass_count,
        "all_cases_passed": pass_count == len(rows),
        "rows": rows,
    }
    results_path = args.results if args.results.is_absolute() else ROOT / args.results
    results_path.parent.mkdir(parents=True, exist_ok=True)
    results_path.write_text(json.dumps(artifact, indent=2, sort_keys=True))

    print_table(rows)
    print(f"\npass_rate={pass_count}/{len(rows)}")
    if args.show_outputs:
        for row in rows:
            print(f"\n===== {row['case_id']} | {row['status']} =====")
            print(row["outcome"]["output"] or "[no output]")
    try:
        display_path = results_path.relative_to(ROOT)
    except ValueError:
        display_path = results_path
    print(f"wrote {display_path}")
    return 0 if pass_count == len(rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())
