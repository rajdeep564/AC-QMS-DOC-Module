"""FastAPI dependencies for API authentication."""

from fastapi import Header, HTTPException

from app.core.config import get_settings


def verify_api_key(x_api_key: str | None = Header(None, alias="X-API-Key")) -> None:
    """Require shared secret on protected routes. Missing or wrong key → 401."""
    settings = get_settings()
    if not x_api_key or x_api_key != settings.api_key:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
