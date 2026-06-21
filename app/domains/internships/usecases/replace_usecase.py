from fastapi import HTTPException, status
from app.domains.internships import repository
from app.domains.user.repository import get_by_email as get_user_by_email
from app.core.email import EmailDeliveryError, build_password_reset_body, send_email
from app.core.jwt import create_reset_token
from app.core.settings import settings
from app.core.security import hash_password
from app.domains.internships.schemas import InternshipsCreate
from app.domains.user.model import User
import secrets


def replace_internship_usecase(db, data: InternshipsCreate):
    """Replace (or create) an internship and optionally a linked user.
    Replicates the router logic, moving all validation and side‑effects here.
    """
    internship = repository.get_by_id(db, data.internship_id)
    if not internship:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campo de estágio não encontrado")

    # verifica e‑mail duplicado se informado
    # Se um e‑mail foi informado, garantir que não exista outro usuário com o mesmo e‑mail
    if data.user_email:
        existing_user = db.query(User).filter(User.email == data.user_email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Já existe um usuário com este e‑mail",
            )
    # atualiza campos principais
    internship.name = data.name
    internship.region_id = data.region_id
    internship.is_active = data.is_active

    # criação opcional de usuário vinculado ao estágio
    if data.user_email:
        temp_password = secrets.token_urlsafe(16)
        user = User(
            name=data.user_name or data.name,
            email=data.user_email,
            password=hash_password(temp_password),
            role="internships",
            internship_id=internship.id,
            is_active=True,
        )
        db.add(user)

    db.commit()

    # envio de e‑mail de redefinição de senha, se necessário
    if data.user_email:
        reset_token = create_reset_token(data.user_email)
        reset_link = f"{settings.FRONTEND_URL.rstrip('/')}/reset-password?token={reset_token}"
        body = build_password_reset_body(reset_link)
        try:
            send_email(data.user_email, "Redefinição de senha", body)
        except EmailDeliveryError as exc:
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc))

    # retorna o estágio atualizado (ou recém‑criado)
    return repository.get_by_id(db, data.internship_id) or internship
