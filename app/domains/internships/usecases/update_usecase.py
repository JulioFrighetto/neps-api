from fastapi import HTTPException, status
from app.domains.internships import repository
from app.domains.user.repository import get_by_email as get_user_by_email
from app.core.email import EmailDeliveryError, build_password_reset_body, send_email
from app.core.jwt import create_reset_token
from app.core.settings import settings
from app.domains.internships.schemas import InternshipsUpdate
from app.domains.user.model import User

def update_internship_usecase(db, data: InternshipsUpdate):
    updated = repository.update(db, data.internship_id, data)

    return updated
