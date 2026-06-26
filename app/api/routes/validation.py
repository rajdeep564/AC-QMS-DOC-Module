from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

from app.schemas.document import TestResultInput, ValidationResponse
from app.validators.acceptance_criteria import validate_test_results

router = APIRouter(prefix="/validation", tags=["validation"])


class ValidateResultsRequest(BaseModel):
    results: list[TestResultInput]


@router.post("/results", response_model=list[ValidationResponse])
def validate_results(request: ValidateResultsRequest):
    payload = [r.model_dump() for r in request.results]
    validated = validate_test_results(payload)
    return [ValidationResponse(**v) for v in validated]
