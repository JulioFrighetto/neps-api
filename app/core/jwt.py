from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt

from app.core.settings import settings

_ALG = settings.ALGORITHM
_SECRET = settings.SECRET_KEY


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def create_access_token(subject: int, extra: dict[str, Any] | None = None) -> str:
    expire = _utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": str(subject), "type": "access", "exp": expire}
    if extra:
        payload.update(extra)
    return jwt.encode(payload, _SECRET, algorithm=_ALG)


def create_refresh_token(subject: int) -> str:
    expire = _utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {"sub": str(subject), "type": "refresh", "exp": expire}
    return jwt.encode(payload, _SECRET, algorithm=_ALG)


def decode_token(token: str) -> dict[str, Any]:
    """Raises JWTError on invalid / expired tokens."""
    return jwt.decode(token, _SECRET, algorithms=[_ALG])
