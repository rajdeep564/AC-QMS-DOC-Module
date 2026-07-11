from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Pharmaceutical QMS Document Platform"
    debug: bool = True

    # SQLite for dev; set DATABASE_URL for PostgreSQL
    database_url: str = f"sqlite:///{BASE_DIR / 'qms.db'}"

    templates_dir: Path = BASE_DIR / "templates"
    generated_dir: Path = BASE_DIR / "generated"
    static_dir: Path = BASE_DIR / "static"
    products_config_dir: Path = BASE_DIR / "config" / "products"

    company_name: str = "Aditya Chemicals"
    default_font: str = "Times New Roman"
    default_font_size: int = 12

    # Shared secret for Gateway → DOC-Module render/generate calls
    api_key: str

    # LibreOffice headless for PDF
    libreoffice_path: str = "soffice"
    pdf_timeout_seconds: int = 120


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.generated_dir.mkdir(parents=True, exist_ok=True)
    settings.templates_dir.mkdir(parents=True, exist_ok=True)
    settings.static_dir.mkdir(parents=True, exist_ok=True)
    settings.products_config_dir.mkdir(parents=True, exist_ok=True)
    return settings
