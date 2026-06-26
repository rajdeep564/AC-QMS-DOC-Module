"""Machine-readable acceptance criteria validation engine."""

from typing import Any

from app.core.constants import ValidationResult
from app.schemas.product import AcceptanceCriteria


def validate_result(
    result_value: str | float | None,
    criteria: AcceptanceCriteria | dict[str, Any] | str | None,
) -> tuple[ValidationResult, str]:
    if result_value is None or result_value == "":
        return ValidationResult.PENDING, "Result not entered"

    if isinstance(criteria, str):
        if str(result_value).strip().lower() == criteria.strip().lower():
            return ValidationResult.PASS, "Matches acceptance criteria"
        return ValidationResult.FAIL, f"Does not match: {criteria}"

    if criteria is None:
        return ValidationResult.PENDING, "No acceptance criteria defined"

    if isinstance(criteria, dict):
        criteria = AcceptanceCriteria.model_validate(criteria)

    try:
        numeric_result = float(result_value)
    except (TypeError, ValueError):
        numeric_result = None

    criteria_type = criteria.type

    if criteria_type == "equals":
        if str(result_value).strip() == str(criteria.value).strip():
            return ValidationResult.PASS, "Matches expected value"
        return ValidationResult.FAIL, f"Expected: {criteria.value}"

    if criteria_type == "text":
        if str(result_value).strip().lower() in str(criteria.value).strip().lower():
            return ValidationResult.PASS, "Text criteria satisfied"
        return ValidationResult.FAIL, f"Expected: {criteria.value}"

    if numeric_result is None:
        return ValidationResult.PENDING, "Numeric result required for this criteria type"

    if criteria_type in ("range", "between"):
        low = criteria.min
        high = criteria.max
        if low is not None and high is not None and low <= numeric_result <= high:
            return ValidationResult.PASS, f"Within range {low} to {high}"
        return ValidationResult.FAIL, f"Outside range {low} to {high}"

    if criteria_type in ("max", "nmt"):
        limit = float(criteria.value) if criteria.value is not None else criteria.max
        if limit is not None and numeric_result <= limit:
            return ValidationResult.PASS, f"NMT {limit}"
        return ValidationResult.FAIL, f"Exceeds NMT {limit}"

    if criteria_type in ("min", "nlt"):
        limit = float(criteria.value) if criteria.value is not None else criteria.min
        if limit is not None and numeric_result >= limit:
            return ValidationResult.PASS, f"NLT {limit}"
        return ValidationResult.FAIL, f"Below NLT {limit}"

    return ValidationResult.PENDING, f"Unsupported criteria type: {criteria_type}"


def validate_test_results(
    results: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    validated: list[dict[str, Any]] = []
    for item in results:
        status, remarks = validate_result(
            item.get("result_value"),
            item.get("acceptance_criteria"),
        )
        validated.append(
            {
                **item,
                "status": status.value,
                "remarks": item.get("remarks") or remarks,
                "acceptance_display": _display_criteria(item.get("acceptance_criteria")),
            }
        )
    return validated


def _display_criteria(criteria: object) -> str:
    if isinstance(criteria, str):
        return criteria
    if isinstance(criteria, dict):
        return AcceptanceCriteria.model_validate(criteria).to_display_string()
    if isinstance(criteria, AcceptanceCriteria):
        return criteria.to_display_string()
    return ""
