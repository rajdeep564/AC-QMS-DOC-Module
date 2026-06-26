import pytest

from app.document_engine.section_numbering import number_sop_sections, number_tests
from app.schemas.product import AcceptanceCriteria
from app.validators.acceptance_criteria import validate_result
from app.core.constants import ValidationResult


def test_section_numbering_flat_tests():
    tests = [{"name": "A"}, {"name": "B"}, {"name": "C"}]
    numbered = number_tests(tests)
    assert numbered[0]["section_no"] == "1.0"
    assert numbered[1]["section_no"] == "2.0"
    assert numbered[2]["section_no"] == "3.0"


def test_section_numbering_nested_tests():
    tests = [
        {
            "name": "Identification",
            "sub_tests": [{"name": "By IR"}, {"name": "By Chemical"}],
        }
    ]
    numbered = number_tests(tests)
    assert numbered[0]["section_no"] == "1.0"
    assert numbered[0]["sub_tests"][0]["section_no"] == "1.1"
    assert numbered[0]["sub_tests"][1]["section_no"] == "1.2"


def test_sop_section_numbering():
    sections = [
        {
            "title": "Objective",
            "subsections": [{"title": "Detail A"}, {"title": "Detail B"}],
        },
        {"title": "Scope"},
    ]
    numbered = number_sop_sections(sections)
    assert numbered[0]["section_no"] == "1.0"
    assert numbered[0]["subsections"][0]["section_no"] == "1.1"
    assert numbered[1]["section_no"] == "2.0"


def test_validate_range_pass():
    status, _ = validate_result(6.1, {"type": "range", "min": 5.9, "max": 6.3})
    assert status == ValidationResult.PASS


def test_validate_range_fail():
    status, _ = validate_result(7.0, {"type": "range", "min": 5.9, "max": 6.3})
    assert status == ValidationResult.FAIL


def test_validate_nmt_pass():
    status, _ = validate_result(5, {"type": "nmt", "value": 10})
    assert status == ValidationResult.PASS


def test_validate_equals_pass():
    status, _ = validate_result("White powder", {"type": "equals", "value": "White powder"})
    assert status == ValidationResult.PASS


def test_acceptance_criteria_display():
    criteria = AcceptanceCriteria(type="range", min=98.5, max=101.5, unit="%")
    assert criteria.to_display_string() == "98.5 to 101.5 %"
