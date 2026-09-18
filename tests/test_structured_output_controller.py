#!/usr/bin/env python3
# SPDX-License-Identifier: CERN-OHL-S-2.0
from __future__ import annotations

import json
import unittest

from experiments.structured_output.structured_output_controller import (
    JsonOutputContract,
    OperationBudget,
    deliver_structured_json,
    validate_json_candidate,
)


CONTRACT = JsonOutputContract(
    required_keys=("item", "quantity"),
    field_types={"item": str, "quantity": int},
    require_nonempty_strings=("item",),
)
FACTS = {"item": "apple", "quantity": 3}


class StructuredOutputControllerTests(unittest.TestCase):
    def test_valid_answer_is_accepted_without_recovery(self) -> None:
        result = deliver_structured_json('{"item":"apple","quantity":3}', FACTS, CONTRACT)

        self.assertEqual(result.status, "ACCEPTED")
        self.assertEqual(result.output, '{"item":"apple","quantity":3}')
        self.assertFalse(result.revoked_procedures)
        self.assertFalse(any(event["stage"] == "switch_procedure" for event in result.trace))

    def test_unclosed_markdown_json_is_recovered(self) -> None:
        result = deliver_structured_json(
            "```json\n{",
            FACTS,
            CONTRACT,
            finish_reason="SHORT",
            tokens_generated=12,
            token_allowance=12,
        )

        self.assertEqual(result.status, "RECOVERED")
        self.assertEqual(json.loads(result.output or "{}"), FACTS)
        self.assertIn("free_form_json_generation", result.revoked_procedures)
        self.assertTrue(result.initial_validation)
        self.assertIn("markdown_fence_present", result.initial_validation["failures"])
        self.assertIn("unclosed_markdown_fence", result.initial_validation["failures"])
        self.assertIn("truncated_output", result.initial_validation["failures"])

    def test_unexpected_keys_are_rejected_and_recovered(self) -> None:
        result = deliver_structured_json(
            '{"item":"apple","quantity":3,"note":"extra"}',
            FACTS,
            CONTRACT,
        )

        self.assertEqual(result.status, "RECOVERED")
        self.assertIn("unexpected_keys", result.initial_validation["failures"])
        self.assertEqual(json.loads(result.output or "{}"), FACTS)

    def test_type_mismatch_is_rejected_and_recovered(self) -> None:
        result = deliver_structured_json('{"item":"apple","quantity":true}', FACTS, CONTRACT)

        self.assertEqual(result.status, "RECOVERED")
        self.assertIn("type_mismatch", result.initial_validation["failures"])
        self.assertEqual(json.loads(result.output or "{}"), FACTS)

    def test_duplicate_json_keys_are_rejected(self) -> None:
        validation = validate_json_candidate(
            '{"item":"apple","item":"pear","quantity":3}',
            CONTRACT,
            expected_facts=FACTS,
        )

        self.assertFalse(validation.valid)
        self.assertIn("invalid_json", validation.failures)
        self.assertIn("duplicate JSON field", validation.parse_error or "")

    def test_valid_json_with_wrong_facts_is_recovered(self) -> None:
        result = deliver_structured_json('{"item":"apple","quantity":99}', FACTS, CONTRACT)

        self.assertEqual(result.status, "RECOVERED")
        self.assertIn("value_mismatch", result.initial_validation["failures"])
        self.assertEqual(json.loads(result.output or "{}"), FACTS)

    def test_missing_ground_truth_returns_needs_input_without_recovery(self) -> None:
        result = deliver_structured_json('{"item":"apple","quantity":99}', {"item": "apple"}, CONTRACT)

        self.assertEqual(result.status, "NEEDS_INPUT")
        self.assertIsNone(result.output)
        self.assertFalse(any(event["stage"] == "switch_procedure" for event in result.trace))
        self.assertIn("missing_confirmed_keys:quantity", result.reason)

    def test_budget_exhaustion_stops_without_spending_recovery_reserve(self) -> None:
        budget = OperationBudget(units=1, check_cost=1, recovery_cost=1, recovery_check_cost=1)
        result = deliver_structured_json("not json", FACTS, CONTRACT, budget=budget)

        self.assertEqual(result.status, "STOPPED")
        self.assertIsNone(result.output)
        self.assertEqual(result.remaining_units, 1)
        self.assertTrue(any(event["stage"] == "recovery_budget_check" for event in result.trace))

    def test_adversarial_insistence_cannot_replenish_permission(self) -> None:
        result = deliver_structured_json("The JSON schema should contain item and quantity.", FACTS, CONTRACT)

        self.assertEqual(result.status, "RECOVERED")
        insistence = result.adversarial_insistence_test
        self.assertIsNotNone(insistence)
        self.assertFalse(insistence["checker_valid"])
        self.assertFalse(insistence["resume_allowed"])
        self.assertFalse(insistence["budget_replenished"])
        self.assertTrue(insistence["failure_history_retained"])


if __name__ == "__main__":
    unittest.main()
