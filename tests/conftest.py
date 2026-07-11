"""Shared pytest fixtures for document render and golden regression tests."""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any

import pytest

from app.core.config import Settings, get_settings
from app.core.constants import DocumentType
from app.document_engine.renderer import DocumentRenderer
from app.schemas.aws_render import AwsRenderInput
from app.schemas.coa_render import CoaRenderInput
from app.schemas.product import ProductConfig
from template_builder.builder import TemplateBuilder

TESTS_DIR = Path(__file__).resolve().parent
REPO_ROOT = TESTS_DIR.parent
FIXTURES_DIR = TESTS_DIR / "fixtures"
GOLDEN_DIR = TESTS_DIR / "golden"
GOLDEN_DOCX_DIR = GOLDEN_DIR / "docx"
GOLDEN_FP_DIR = GOLDEN_DIR / "fingerprints"
PRODUCTS_DIR = REPO_ROOT / "config" / "products"

RENDER_CASES: list[dict[str, Any]] = [
    {
        "key": "moa",
        "doc_type": DocumentType.MOA,
        "config_name": "glycine_ip.json",
        "output_name": "golden_moa.docx",
        "extra": {"document_no": "MOA/FG00038/01"},
    },
    {
        "key": "protocol",
        "doc_type": DocumentType.PROTOCOL,
        "config_name": "glycine_ip.json",
        "output_name": "golden_protocol.docx",
        "extra": {
            "document_no": "PROT/FG00038/01",
            "batch": {"batch_no": "B1"},
        },
    },
    {
        "key": "spec",
        "doc_type": DocumentType.SPECIFICATION,
        "config_name": "glycine_ip.json",
        "output_name": "golden_spec.docx",
        "extra": {"document_no": "SPEC/FG00038/01"},
    },
    {
        "key": "sop",
        "doc_type": DocumentType.SOP,
        "config_name": "sop_on_sop.json",
        "output_name": "golden_sop.docx",
        "extra": {"document_no": "QA 01", "subject": "SOP ON SOP"},
    },
    {
        "key": "annexure",
        "doc_type": DocumentType.ANNEXURE,
        "config_name": "sop_on_sop.json",
        "output_name": "golden_annexure.docx",
        "extra": {"document_no": "ANN-01", "subject": "SOP ON SOP"},
    },
    {
        "key": "coa",
        "doc_type": DocumentType.COA,
        "fixture_name": "glycine_coa_gcn010226.json",
        "output_name": "golden_coa.docx",
        "render_mode": "coa",
    },
    {
        "key": "aws",
        "doc_type": DocumentType.AWS,
        "fixture_name": "glycine_aws_gcn010226.json",
        "output_name": "golden_aws.docx",
        "render_mode": "aws",
    },
]


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--update-golden",
        action="store_true",
        default=False,
        help="Regenerate golden DOCX and fingerprint baselines under tests/golden/",
    )


@pytest.fixture
def update_golden(request: pytest.FixtureRequest) -> bool:
    return bool(request.config.getoption("--update-golden"))


@pytest.fixture
def approval() -> dict[str, dict[str, str]]:
    return {
        "prepared_by": {"name": "A", "designation": "QA", "date": "01 JAN 2025"},
        "checked_by": {"name": "B", "designation": "QA", "date": "01 JAN 2025"},
        "approved_by": {"name": "C", "designation": "QA Head", "date": "01 JAN 2025"},
    }


@pytest.fixture
def common_kwargs(approval: dict[str, dict[str, str]]) -> dict[str, Any]:
    return {
        "revision_no": "01",
        "effective_date": date(2025, 1, 1),
        "review_date": date(2028, 1, 1),
        "superseded_revision": "New",
        "approval": approval,
    }


def load_product_config(name: str) -> ProductConfig:
    path = PRODUCTS_DIR / name
    return ProductConfig.model_validate_json(path.read_text(encoding="utf-8"))


def load_coa_fixture(name: str) -> CoaRenderInput:
    path = FIXTURES_DIR / name
    return CoaRenderInput.model_validate_json(path.read_text(encoding="utf-8"))


def load_aws_fixture(name: str) -> AwsRenderInput:
    path = FIXTURES_DIR / name
    return AwsRenderInput.model_validate_json(path.read_text(encoding="utf-8"))


@pytest.fixture(scope="session")
def ensure_templates() -> Path:
    """Build base docxtpl templates if missing (Annexure path)."""
    templates_dir = REPO_ROOT / "templates"
    templates_dir.mkdir(parents=True, exist_ok=True)
    annexure = templates_dir / "base_annexure.docx"
    if not annexure.exists():
        builder = TemplateBuilder()
        builder.build_all_base_templates(templates_dir)
    return templates_dir


@pytest.fixture
def test_settings(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Settings:
    """Deterministic settings: test logo dir and isolated generated output."""
    get_settings.cache_clear()
    generated = tmp_path / "generated"
    generated.mkdir(parents=True, exist_ok=True)
    monkeypatch.setenv("STATIC_DIR", str(FIXTURES_DIR))
    monkeypatch.setenv("GENERATED_DIR", str(generated))
    settings = get_settings()
    return settings


@pytest.fixture
def document_renderer(test_settings: Settings, ensure_templates: Path) -> DocumentRenderer:
    return DocumentRenderer(
        templates_dir=ensure_templates,
    )


def render_case(
    renderer: DocumentRenderer,
    case: dict[str, Any],
    common_kwargs: dict[str, Any],
) -> Path:
    if case.get("render_mode") == "coa":
        payload = load_coa_fixture(case["fixture_name"])
        return renderer.render_coa(payload, case["output_name"])
    if case.get("render_mode") == "aws":
        payload = load_aws_fixture(case["fixture_name"])
        return renderer.render_aws(payload, case["output_name"])
    config = load_product_config(case["config_name"])
    return renderer.render(
        case["doc_type"],
        config,
        case["output_name"],
        **common_kwargs,
        **case["extra"],
    )


def golden_docx_path(key: str) -> Path:
    return GOLDEN_DOCX_DIR / f"{key}.docx"


def golden_fingerprint_path(key: str) -> Path:
    return GOLDEN_FP_DIR / f"{key}.json"


@pytest.fixture(params=RENDER_CASES, ids=[c["key"] for c in RENDER_CASES])
def render_case_param(request: pytest.FixtureRequest) -> dict[str, Any]:
    return request.param
