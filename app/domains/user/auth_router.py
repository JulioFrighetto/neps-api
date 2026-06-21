import logging

from fastapi import APIRouter, Depends, HTTPException, status
from jose import JWTError
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.email import EmailDeliveryError, build_password_reset_body, send_email
from app.core.deps import get_current_user
from app.core.jwt import (
    create_access_token,
    create_refresh_token,
    create_reset_token,
    decode_reset_token,
    decode_token,
)
from app.core.settings import settings
from app.domains.user import repository
from app.domains.user.schemas import (
    LoginRequest,
    RefreshRequest,
    PasswordResetConfirmRequest,
    PasswordResetRequest,
    TestEmailRequest,
    TokenResponse,
    UserResponse,
)

router = APIRouter(prefix="/auth", tags=["Auth"])
logger = logging.getLogger(__name__)


def _build_access_token_extra(user) -> dict[str, int | str | None]:
    return {
        "role": user.role,
        "user_name": user.name,
        "internship_id": user.internship_id,
        "internships_name": user.internships.name if user.internships else None,
        "education_institute_id": user.education_institute_id,
        "education_institute_name": (
            user.education_institute.name if user.education_institute else None
        ),
    }


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    existing = repository.get_by_email(db, data.email)
    if existing and not existing.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário inativo",
        )

    user = repository.authenticate(db, data.email, data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas",
        )
    return TokenResponse(
        access_token=create_access_token(
            user.id,
            role=user.role,
            extra=_build_access_token_extra(user),
        ),
        refresh_token=create_refresh_token(user.id),
    )


@router.post("/refresh", response_model=TokenResponse)
def refresh(data: RefreshRequest, db: Session = Depends(get_db)):
    try:
        payload = decode_token(data.refresh_token)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token inválido ou expirado",
        )
    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token fornecido não é um refresh token",
        )
    user = repository.get_by_id(db, int(payload["sub"]))
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não encontrado ou inativo",
        )
    return TokenResponse(
        access_token=create_access_token(
            user.id,
            role=user.role,
            extra=_build_access_token_extra(user),
        ),
        refresh_token=create_refresh_token(user.id),
    )


@router.post("/reset-password", status_code=status.HTTP_204_NO_CONTENT)
def request_password_reset(
    data: PasswordResetRequest,
    db: Session = Depends(get_db),
):
    logger.info("Password reset requested", extra={"email": data.email})
    user = repository.get_by_email(db, data.email)
    if not user or not user.is_active:
        logger.warning("Password reset rejected: user not found or inactive", extra={"email": data.email})
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado ou inativo",
        )

    reset_token = create_reset_token(user.email)
    reset_link = f"{settings.FRONTEND_URL.rstrip('/')}/reset-password?token={reset_token}"
    subject = "Redefinição de senha"
    body = build_password_reset_body(reset_link)

    try:
        send_email(user.email, subject, body)
    except EmailDeliveryError as exc:
        logger.exception("Password reset email delivery failed", extra={"email": user.email})
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        )


@router.post("/reset-password-confirm", status_code=status.HTTP_204_NO_CONTENT)
@router.post("/reset-password/confirm", status_code=status.HTTP_204_NO_CONTENT)
def confirm_password_reset(data: PasswordResetConfirmRequest, db: Session = Depends(get_db)):
    try:
        payload = decode_reset_token(data.reset_hash)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de recuperação inválido ou expirado",
        )

    user = repository.get_by_email(db, payload["email"])
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado ou inativo",
        )

    repository.reset_password(db, user.id, data.new_password)


@router.post("/test-email", status_code=status.HTTP_204_NO_CONTENT)
def test_email(data: TestEmailRequest):
    subject = "Teste de envio de e-mail"
    body = (
        "Este é um e-mail de teste da API NEPS.\n\n"
        "Se você recebeu esta mensagem, a configuração SMTP está funcionando."
    )

    try:
        send_email(data.email, subject, body)
    except EmailDeliveryError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        )
