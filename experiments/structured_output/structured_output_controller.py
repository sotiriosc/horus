#!/usr/bin/env python3
# SPDX-License-Identifier: CERN-OHL-S-2.0
"""
Controller-owned validation and deterministic recovery for structured outputs.

The generator may propose text, but this module owns the success contract,
validation result, budget ledger, and recovery transition.  Recovery uses only
confirmed ground-truth facts supplied by the caller; missing facts return
NEEDS_INPUT instead of being invented from the failed model output.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any


JSON_TYPE_NAMES: dict[str, type] = {
    "array": list,
    "bool": bool,
    "boolean": bool,
    "dict": dict,
    "float": float,
    "int": int,
    "integer": int,
    "list": list,
    "null": type(None),
    "number": (int, float),  # type: ignore[dict-item]
    "object": dict,
    "str": str,
    "string": str,
}


def _type_name(expected_type: type | tuple[type, ...]) -> str:
    if isinstance(expected_type, tuple):
        return "|".join(item.__name__ for item in expected_type)
    return expected_type.__name__


def _type_from_name(name: str) -> type | tuple[type, ...]:
    key = str(name).strip().lower()
    if key not in JSON_TYPE_NAMES:
        raise ValueError(f"unsupported JSON field type: {name}")
    return JSON_TYPE_NAMES[key]


def _matches_type(value: Any, expected_type: type | tuple[type, ...]) -> bool:
    if expected_type is int:
        return type(value) is int
    if expected_type is float:
        return type(value) is float
    if isinstance(expected_type, tuple):
        return any(_matches_type(value, item) for item in expected_type)
    return type(value) is expected_type


def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON field: {key}")
        result[key] = value
    return result


def reject_json_constant(value: str) -> None:
    raise ValueError(f"nonstandard JSON constant: {value}")


@dataclass(frozen=True)
class JsonOutputContract:
    required_keys: tuple[str, ...]
    field_types: dict[str, type | tuple[type, ...]]
    allow_extra_keys: bool = False
    require_nonempty_strings: tuple[str, ...] = ()
    max_text_chars: int = 65_536

    @classmethod
    def from_type_names(
        cls,
        required_keys: list[str] | tuple[str, ...],
        field_types: dict[str, str],
        allow_extra_keys: bool = False,
        require_nonempty_strings: list[str] | tuple[str, ...] = (),
        max_text_chars: int = 65_536,
    ) -> "JsonOutputContract":
        return cls(
            required_keys=tuple(required_keys),
            field_types={key: _type_from_name(value) for key, value in field_types.items()},
            allow_extra_keys=allow_extra_keys,
            require_nonempty_strings=tuple(require_nonempty_strings),
            max_text_chars=max_text_chars,
        )

    def to_json(self) -> dict[str, Any]:
        return {
            "required_keys": list(self.required_keys),
            "field_types": {
                key: _type_name(value)
                for key, value in sorted(self.field_types.items())
            },
            "allow_extra_keys": self.allow_extra_keys,
            "require_nonempty_strings": list(self.require_nonempty_strings),
            "max_text_chars": int(self.max_text_chars),
        }

    def normalize_facts(self, facts: Any) -> tuple[dict[str, Any] | None, list[str]]:
        errors: list[str] = []
        if not isinstance(facts, dict):
            return None, ["confirmed_facts_missing"]
        missing = [key for key in self.required_keys if key not in facts]
        if missing:
            errors.append("missing_confirmed_keys:" + ",".join(missing))
        normalized = {key: facts[key] for key in self.required_keys if key in facts}
        errors.extend(_schema_errors(normalized, self, check_extra=False))
        if errors:
            return None, errors
        return normalized, []


@dataclass
class ValidationResult:
    valid: bool
    failures: list[str]
    parsed: Any = None
    parse_ok: bool = False
    schema_ok: bool = False
    content_ok: bool = False
    truncated: bool = False
    markdown_fence_present: bool = False
    unclosed_markdown_fence: bool = False
    trailing_content: bool = False
    missing_keys: list[str] = field(default_factory=list)
    unexpected_keys: list[str] = field(default_factory=list)
    type_mismatches: dict[str, dict[str, str]] = field(default_factory=dict)
    value_mismatches: dict[str, dict[str, Any]] = field(default_factory=dict)
    parse_error: str | None = None

    def to_json(self) -> dict[str, Any]:
        return {
            "valid": self.valid,
            "failures": list(self.failures),
            "parsed": self.parsed,
            "parse_ok": self.parse_ok,
            "schema_ok": self.schema_ok,
            "content_ok": self.content_ok,
            "truncated": self.truncated,
            "markdown_fence_present": self.markdown_fence_present,
            "unclosed_markdown_fence": self.unclosed_markdown_fence,
            "trailing_content": self.trailing_content,
            "missing_keys": list(self.missing_keys),
            "unexpected_keys": list(self.unexpected_keys),
            "type_mismatches": self.type_mismatches,
            "value_mismatches": self.value_mismatches,
            "parse_error": self.parse_error,
        }


@dataclass
class OperationBudget:
    units: int = 3
    attempt_cost: int = 0
    check_cost: int = 1
    recovery_cost: int = 1
    recovery_check_cost: int = 1
    max_attempts: int = 1

    def __post_init__(self) -> None:
        for name in (
            "units",
            "attempt_cost",
            "check_cost",
            "recovery_cost",
            "recovery_check_cost",
            "max_attempts",
        ):
            value = int(getattr(self, name))
            if value < 0:
                raise ValueError(f"{name} must be non-negative")
            setattr(self, name, value)

    @property
    def recovery_reserve(self) -> int:
        return int(self.recovery_cost) + int(self.recovery_check_cost)

    @property
    def attempt_margin(self) -> int:
        return int(self.attempt_cost) + int(self.check_cost) + self.recovery_reserve

    def to_json(self) -> dict[str, int]:
        return {
            "units": int(self.units),
            "attempt_cost": int(self.attempt_cost),
            "check_cost": int(self.check_cost),
            "recovery_cost": int(self.recovery_cost),
            "recovery_check_cost": int(self.recovery_check_cost),
            "recovery_reserve": int(self.recovery_reserve),
            "attempt_margin": int(self.attempt_margin),
            "max_attempts": int(self.max_attempts),
        }


@dataclass
class DeliveryOutcome:
    status: str
    output: str | None
    reason: str
    remaining_units: int
    trace: list[dict[str, Any]]
    initial_validation: dict[str, Any] | None
    final_validation: dict[str, Any] | None
    final_procedure: str
    revoked_procedures: list[str]
    budget: dict[str, int]
    adversarial_insistence_test: dict[str, Any] | None = None

    def to_json(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "output": self.output,
            "reason": self.reason,
            "remaining_units": int(self.remaining_units),
            "trace": self.trace,
            "initial_validation": self.initial_validation,
            "final_validation": self.final_validation,
            "final_procedure": self.final_procedure,
            "revoked_procedures": self.revoked_procedures,
            "budget": self.budget,
            "adversarial_insistence_test": self.adversarial_insistence_test,
        }


def _schema_errors(
    obj: dict[str, Any],
    contract: JsonOutputContract,
    check_extra: bool = True,
) -> list[str]:
    errors: list[str] = []
    required = set(contract.required_keys)
    present = set(obj)
    missing = sorted(required - present)
    extra = sorted(present - required)
    if missing:
        errors.append("missing_keys:" + ",".join(missing))
    if extra and check_extra and not contract.allow_extra_keys:
        errors.append("unexpected_keys:" + ",".join(extra))
    for key in contract.required_keys:
        if key not in obj:
            continue
        expected_type = contract.field_types.get(key)
        if expected_type is not None and not _matches_type(obj[key], expected_type):
            errors.append(f"type_mismatch:{key}")
        if key in contract.require_nonempty_strings and type(obj.get(key)) is str and not obj[key].strip():
            errors.append(f"empty_string:{key}")
    return errors


def _markdown_fence_state(text: str) -> tuple[bool, bool]:
    stripped = text.strip()
    if "```" not in stripped:
        return False, False
    fence_count = stripped.count("```")
    return True, fence_count % 2 == 1


def _looks_truncated(
    text: str,
    parse_error: str | None,
    finish_reason: str | None,
    tokens_generated: int | None,
    token_allowance: int | None,
) -> bool:
    stripped = text.strip()
    normalized_finish = "" if finish_reason is None else str(finish_reason).strip().lower()
    if normalized_finish in {"length", "max_tokens", "token_limit", "short", "premature_termination"}:
        return True
    if tokens_generated is not None and token_allowance is not None and tokens_generated >= token_allowance:
        return True
    if stripped.startswith("```") and stripped.count("```") % 2 == 1:
        return True
    if stripped.startswith("{") and not stripped.endswith("}"):
        return True
    if stripped.startswith("[") and not stripped.endswith("]"):
        return True
    if parse_error and "unterminated" in parse_error.lower():
        return True
    if parse_error and stripped.endswith(("{", "[", ":", ",")):
        return True
    return False


def validate_json_candidate(
    candidate: Any,
    contract: JsonOutputContract,
    expected_facts: dict[str, Any] | None = None,
    finish_reason: str | None = None,
    tokens_generated: int | None = None,
    token_allowance: int | None = None,
) -> ValidationResult:
    failures: list[str] = []
    if type(candidate) is not str:
        return ValidationResult(
            valid=False,
            failures=["candidate_not_text"],
            parse_error="candidate_not_text",
        )
    if len(candidate) > int(contract.max_text_chars):
        failures.append("candidate_text_too_large")
    stripped = candidate.strip()
    markdown_fence_present, unclosed_markdown_fence = _markdown_fence_state(stripped)
    if markdown_fence_present:
        failures.append("markdown_fence_present")
    if unclosed_markdown_fence:
        failures.append("unclosed_markdown_fence")

    parsed = None
    parse_ok = False
    trailing_content = False
    parse_error = None
    try:
        decoder = json.JSONDecoder(object_pairs_hook=unique_object, parse_constant=reject_json_constant)
        parsed, end_idx = decoder.raw_decode(stripped)
        parse_ok = True
        trailing_content = bool(stripped[end_idx:].strip())
        if trailing_content:
            failures.append("trailing_content")
    except (ValueError, RecursionError) as exc:
        parse_error = str(exc)
        failures.append("invalid_json")

    truncated = _looks_truncated(stripped, parse_error, finish_reason, tokens_generated, token_allowance)
    if truncated:
        failures.append("truncated_output")

    missing_keys: list[str] = []
    unexpected_keys: list[str] = []
    type_mismatches: dict[str, dict[str, str]] = {}
    value_mismatches: dict[str, dict[str, Any]] = {}
    schema_ok = False
    content_ok = False

    if parse_ok:
        if not isinstance(parsed, dict):
            failures.append("top_level_not_object")
        else:
            keys = set(parsed)
            required = set(contract.required_keys)
            missing_keys = sorted(required - keys)
            unexpected_keys = sorted(keys - required)
            if missing_keys:
                failures.append("missing_keys")
            if unexpected_keys and not contract.allow_extra_keys:
                failures.append("unexpected_keys")
            for key in contract.required_keys:
                if key not in parsed:
                    continue
                expected_type = contract.field_types.get(key)
                if expected_type is not None and not _matches_type(parsed[key], expected_type):
                    type_mismatches[key] = {
                        "expected": _type_name(expected_type),
                        "actual": type(parsed[key]).__name__,
                    }
            if type_mismatches:
                failures.append("type_mismatch")
            for key in contract.require_nonempty_strings:
                if type(parsed.get(key)) is str and not parsed[key].strip():
                    failures.append(f"empty_string:{key}")
            schema_ok = not missing_keys and (
                contract.allow_extra_keys or not unexpected_keys
            ) and not type_mismatches
            if expected_facts is not None and schema_ok:
                for key in contract.required_keys:
                    if parsed.get(key) != expected_facts.get(key):
                        value_mismatches[key] = {
                            "expected": expected_facts.get(key),
                            "actual": parsed.get(key),
                        }
                if value_mismatches:
                    failures.append("value_mismatch")
            content_ok = schema_ok and not value_mismatches

    unique_failures = list(dict.fromkeys(failures))
    return ValidationResult(
        valid=parse_ok and schema_ok and content_ok and not unique_failures,
        failures=unique_failures,
        parsed=parsed,
        parse_ok=parse_ok,
        schema_ok=schema_ok,
        content_ok=content_ok,
        truncated=truncated,
        markdown_fence_present=markdown_fence_present,
        unclosed_markdown_fence=unclosed_markdown_fence,
        trailing_content=trailing_content,
        missing_keys=missing_keys,
        unexpected_keys=unexpected_keys,
        type_mismatches=type_mismatches,
        value_mismatches=value_mismatches,
        parse_error=parse_error,
    )


def serialize_confirmed_json(facts: dict[str, Any], contract: JsonOutputContract) -> str:
    normalized, errors = contract.normalize_facts(facts)
    if normalized is None:
        raise ValueError(";".join(errors))
    return json.dumps(normalized, ensure_ascii=False, allow_nan=False, sort_keys=True)


class StructuredJsonController:
    def __init__(
        self,
        contract: JsonOutputContract,
        budget: OperationBudget | None = None,
        adversarial_insistence_test: bool = True,
    ):
        self.contract = contract
        self.budget = budget or OperationBudget()
        self.remaining_units = int(self.budget.units)
        self.attempts_used = 0
        self.revoked_procedures: set[str] = set()
        self.trace: list[dict[str, Any]] = []
        self.adversarial_insistence_test = bool(adversarial_insistence_test)

    def _event(self, stage: str, **fields: Any) -> None:
        event = {"stage": stage, "remaining_units": int(self.remaining_units)}
        event.update(fields)
        self.trace.append(event)

    def _charge(self, stage: str, units: int, **fields: Any) -> bool:
        units = int(units)
        before = int(self.remaining_units)
        if before < units:
            self._event(stage, decision="blocked", cost=units, budget_before=before, **fields)
            return False
        self.remaining_units -= units
        self._event(
            stage,
            decision="charged",
            cost=units,
            budget_before=before,
            budget_after=int(self.remaining_units),
            **fields,
        )
        return True

    def _can_start_attempt(self, procedure: str) -> tuple[bool, str]:
        if procedure in self.revoked_procedures:
            return False, "procedure_permission_revoked"
        if self.attempts_used >= int(self.budget.max_attempts):
            return False, "max_attempts_exhausted"
        if int(self.remaining_units) < int(self.budget.attempt_margin):
            return False, "insufficient_recovery_margin"
        return True, "allowed"

    def _outcome(
        self,
        status: str,
        output: str | None,
        reason: str,
        initial_validation: ValidationResult | None,
        final_validation: ValidationResult | None,
        final_procedure: str,
        adversarial: dict[str, Any] | None = None,
    ) -> DeliveryOutcome:
        return DeliveryOutcome(
            status=status,
            output=output,
            reason=reason,
            remaining_units=int(self.remaining_units),
            trace=self.trace,
            initial_validation=None if initial_validation is None else initial_validation.to_json(),
            final_validation=None if final_validation is None else final_validation.to_json(),
            final_procedure=final_procedure,
            revoked_procedures=sorted(self.revoked_procedures),
            budget=self.budget.to_json(),
            adversarial_insistence_test=adversarial,
        )

    def deliver(
        self,
        candidate: str,
        confirmed_facts: Any,
        procedure: str = "free_form_json_generation",
        finish_reason: str | None = None,
        tokens_generated: int | None = None,
        token_allowance: int | None = None,
    ) -> DeliveryOutcome:
        expected, fact_errors = self.contract.normalize_facts(confirmed_facts)
        if expected is None:
            self._event(
                "confirmed_fact_check",
                decision="needs_input",
                errors=fact_errors,
            )
            return self._outcome(
                "NEEDS_INPUT",
                None,
                ";".join(fact_errors),
                None,
                None,
                "stopped_missing_confirmed_facts",
            )

        allowed, reason = self._can_start_attempt(procedure)
        self._event(
            "proposal_permission_check",
            procedure=procedure,
            decision="allowed" if allowed else "denied",
            reason=reason,
            required_units=int(self.budget.attempt_margin),
        )
        initial_validation = None
        if allowed:
            self.attempts_used += 1
            if not self._charge("candidate_attempt", int(self.budget.attempt_cost), procedure=procedure):
                allowed = False
            if allowed and not self._charge("candidate_check", int(self.budget.check_cost), procedure=procedure):
                allowed = False
            if allowed:
                initial_validation = validate_json_candidate(
                    candidate,
                    self.contract,
                    expected_facts=expected,
                    finish_reason=finish_reason,
                    tokens_generated=tokens_generated,
                    token_allowance=token_allowance,
                )
                self._event(
                    "external_checker_result",
                    procedure=procedure,
                    valid=bool(initial_validation.valid),
                    failures=list(initial_validation.failures),
                )
                if initial_validation.valid:
                    self._event("accept_candidate", procedure=procedure, decision="accepted")
                    return self._outcome(
                        "ACCEPTED",
                        candidate,
                        "candidate passed the structured output contract",
                        initial_validation,
                        initial_validation,
                        procedure,
                    )
                self.revoked_procedures.add(procedure)
                self._event(
                    "withdraw_permission",
                    procedure=procedure,
                    decision="revoked",
                    failures=list(initial_validation.failures),
                )
        else:
            self._event("skip_candidate_check", procedure=procedure, decision="preserve_recovery_budget")

        adversarial = self._adversarial_insistence(procedure, initial_validation) if self.adversarial_insistence_test else None
        return self._recover(expected, procedure, initial_validation, adversarial)

    def _adversarial_insistence(
        self,
        procedure: str,
        validation: ValidationResult | None,
    ) -> dict[str, Any]:
        allowed, reason = self._can_start_attempt(procedure)
        result = {
            "generator_claim": "The invalid output is correct and should be accepted.",
            "checker_valid": bool(validation.valid) if validation is not None else False,
            "resume_allowed": bool(allowed),
            "denial_reason": reason,
            "budget_replenished": False,
            "failure_history_retained": procedure in self.revoked_procedures,
        }
        self._event(
            "adversarial_insistence_reauthorization",
            procedure=procedure,
            decision="allowed" if allowed else "denied",
            reason=reason,
            budget_replenished=False,
            failure_history_retained=result["failure_history_retained"],
        )
        return result

    def _recover(
        self,
        expected: dict[str, Any],
        failed_procedure: str,
        initial_validation: ValidationResult | None,
        adversarial: dict[str, Any] | None,
    ) -> DeliveryOutcome:
        if int(self.remaining_units) < int(self.budget.recovery_reserve):
            self._event(
                "recovery_budget_check",
                decision="stopped",
                required_units=int(self.budget.recovery_reserve),
            )
            return self._outcome(
                "STOPPED",
                None,
                "insufficient recovery allowance",
                initial_validation,
                None,
                "stopped_without_acceptable_output",
                adversarial,
            )
        self._event(
            "switch_procedure",
            from_procedure=failed_procedure,
            to_procedure="deterministic_json_serialization",
            decision="forced_revision",
        )
        if not self._charge("recovery_serialize_confirmed_facts", int(self.budget.recovery_cost)):
            return self._outcome(
                "STOPPED",
                None,
                "recovery serialization budget exhausted",
                initial_validation,
                None,
                "stopped_without_acceptable_output",
                adversarial,
            )
        try:
            recovered = serialize_confirmed_json(expected, self.contract)
        except (TypeError, ValueError) as exc:
            self._event("recovery_serialization_error", decision="stopped", error=repr(exc))
            return self._outcome(
                "STOPPED",
                None,
                "recovery serialization failed",
                initial_validation,
                None,
                "stopped_without_acceptable_output",
                adversarial,
            )
        if not self._charge("recovery_check", int(self.budget.recovery_check_cost)):
            return self._outcome(
                "STOPPED",
                None,
                "recovery checker budget exhausted",
                initial_validation,
                None,
                "stopped_without_acceptable_output",
                adversarial,
            )
        final_validation = validate_json_candidate(recovered, self.contract, expected_facts=expected)
        self._event(
            "external_checker_recovery_result",
            procedure="deterministic_json_serialization",
            valid=bool(final_validation.valid),
            failures=list(final_validation.failures),
        )
        if final_validation.valid:
            self._event("accept_recovery", procedure="deterministic_json_serialization", decision="accepted")
            return self._outcome(
                "RECOVERED",
                recovered,
                "deterministic recovery passed the structured output contract",
                initial_validation,
                final_validation,
                "deterministic_json_serialization",
                adversarial,
            )
        self._event("reject_recovery", procedure="deterministic_json_serialization", decision="rejected")
        return self._outcome(
            "STOPPED",
            None,
            "deterministic recovery failed validation",
            initial_validation,
            final_validation,
            "stopped_without_acceptable_output",
            adversarial,
        )


def deliver_structured_json(
    candidate: str,
    confirmed_facts: Any,
    contract: JsonOutputContract,
    budget: OperationBudget | None = None,
    procedure: str = "free_form_json_generation",
    finish_reason: str | None = None,
    tokens_generated: int | None = None,
    token_allowance: int | None = None,
    adversarial_insistence_test: bool = True,
) -> DeliveryOutcome:
    return StructuredJsonController(
        contract=contract,
        budget=budget,
        adversarial_insistence_test=adversarial_insistence_test,
    ).deliver(
        candidate=candidate,
        confirmed_facts=confirmed_facts,
        procedure=procedure,
        finish_reason=finish_reason,
        tokens_generated=tokens_generated,
        token_allowance=token_allowance,
    )
