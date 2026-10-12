import secrets

from fastapi import Depends, HTTPException
from fastapi.security import APIKeyHeader

from app.config import settings

API_KEY_HEADER = "X-API-Key"

_scheme = APIKeyHeader(name=API_KEY_HEADER, auto_error=False)


def require_api_key(provided: str | None = Depends(_scheme)) -> None:
    """Gate for every write route.

    Fails closed: with no API_KEY in the environment the route refuses the write
    instead of accepting it. An unconfigured deployment is a deployment nobody
    can write to, which is the safe end of that mistake. CORS is no substitute,
    because it only restrains browsers - curl ignores it.
    """
    if not settings.api_key:
        raise HTTPException(503, "writes are disabled: API_KEY is not configured")
    if not provided:
        raise HTTPException(401, f"missing {API_KEY_HEADER} header")
    if not secrets.compare_digest(provided, settings.api_key):
        raise HTTPException(401, "invalid API key")
