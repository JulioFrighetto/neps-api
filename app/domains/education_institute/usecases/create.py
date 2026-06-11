import logging

from sqlalchemy.orm import Session

from app.core.settings import settings
from app.core.email import EmailDeliveryError, build_welcome_body, send_email
from app.core.jwt import create_reset_token
from app.domains.education_institute import repository
from app.domains.education_institute.schemas import EducationInstituteCreate

logger = logging.getLogger(__name__)


def create_usecase(db: Session, data: EducationInstituteCreate):
    institute = repository.create(db, data)
    target_email = data.user_email or data.email
    if target_email:
        reset_token = create_reset_token(target_email)
        reset_link = f"{settings.FRONTEND_URL.rstrip('/')}/reset-password?token={reset_token}"
        body = build_welcome_body(reset_link, data.user_name or institute.name)
        try:
            send_email(target_email, "Bem-vindo ao NEPS", body)
        except EmailDeliveryError as exc:
            logger.error("Falha ao enviar e-mail de boas-vindas para %s: %s", target_email, exc)
    return institute
