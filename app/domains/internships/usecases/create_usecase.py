from fastapi import HTTPException, status
from app.domains.internships import repository
from app.domains.user.repository import get_by_email as get_user_by_email
from app.core.email import EmailDeliveryError, build_welcome_body, send_email
from app.core.jwt import create_reset_token
from app.core.settings import settings
from app.domains.internships.schemas import InternshipsCreate


def create_internship_usecase(db, data: InternshipsCreate):
    """Create internship with optional welcome email.
    Mirrors router validation and side‑effects.
    """
    if repository.get_by_name(db, data.name):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Já existe um campo de estágio com este nome",
        )
    if data.user_email and get_user_by_email(db, data.user_email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Já existe um usuário com este e-mail",
        )

    internship = repository.create(db, data)
    if data.user_email:
        reset_token = create_reset_token(data.user_email)
        reset_link = f"{settings.FRONTEND_URL.rstrip('/')}/reset-password?token={reset_token}"
        body = build_welcome_body(reset_link, data.user_name or data.name)
        try:
            send_email(data.user_email, "Bem-vindo ao NEPS", body)
        except EmailDeliveryError:
            # ignore email failures in dev/test environments
            pass
    return internship
