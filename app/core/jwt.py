import base64
import json
from datetime import datetime, timedelta, timezone
from hashlib import sha256
from typing import Any

from cryptography.fernet import Fernet, InvalidToken
from jose import JWTError, jwt

from app.core.settings import settings

_ALG = settings.ALGORITHM
_SECRET = settings.SECRET_KEY


def _fernet() -> Fernet:
    key = base64.urlsafe_b64encode(sha256(_SECRET.encode("utf-8")).digest())
    return Fernet(key)


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


def create_reset_token(email: str) -> str:
    payload = {
        "email": email,
        "requested_at": _utcnow().isoformat(),
    }
    token_bytes = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    return _fernet().encrypt(token_bytes).decode("utf-8")


def decode_reset_token(token: str) -> dict[str, Any]:
    try:
        decrypted = _fernet().decrypt(token.encode("utf-8"))
    except InvalidToken as exc:
        raise JWTError("Reset token inválido ou expirado") from exc

    payload = json.loads(decrypted.decode("utf-8"))
    requested_at = datetime.fromisoformat(payload["requested_at"])
    age = _utcnow() - requested_at
    if age > timedelta(minutes=settings.RESET_TOKEN_EXPIRE_MINUTES):
        raise JWTError("Reset token inválido ou expirado")
    if age < timedelta(minutes=-1):
        raise JWTError("Reset token inválido ou expirado")
    return payload


def decode_token(token: str) -> dict[str, Any]:
    """Raises JWTError on invalid / expired tokens."""
    return jwt.decode(token, _SECRET, algorithms=[_ALG])
