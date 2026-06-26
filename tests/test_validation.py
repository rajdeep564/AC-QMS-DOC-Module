import pytest

from app.validators.acceptance_criteria import validate_test_results


def test_validate_batch_results():
    results = [
        {
            "test_name": "pH",
            "result_value": 6.1,
            "acceptance_criteria": {"type": "range", "min": 5.9, "max": 6.3},
        },
        {
            "test_name": "Assay",
            "result_value": 102.0,
            "acceptance_criteria": {"type": "range", "min": 98.5, "max": 101.5},
        },
    ]
    validated = validate_test_results(results)
    assert validated[0]["status"] == "PASS"
    assert validated[1]["status"] == "FAIL"
