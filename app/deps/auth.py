import secrets
from typing import Annotated

from fastapi import Header, HTTPException

from app.settings import settings


def require_api_key(x_api_key: Annotated[str | None, Header()] = None) -> None:
    if x_api_key is None or not secrets.compare_digest(x_api_key, settings.auth.api_key):
        raise HTTPException(status_code=401, detail="Invalid API key")
