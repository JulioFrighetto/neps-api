from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.email import (
    EmailDeliveryError,
    build_password_reset_body,
    build_welcome_body,
    send_email,
)
from app.core.jwt import create_reset_token
from app.core.schemas import Page
from app.core.settings import settings
from app.domains.service import repository
from app.domains.service.schemas import ServiceCreate, ServiceResponse, ServiceUpdate
from app.domains.user.model import User
from app.domains.user.repository import get_by_email as get_user_by_email
from app.core.security import hash_password
import secrets

router = APIRouter(prefix="/services", tags=["Services"])


@router.get("/", response_model=Page[ServiceResponse])
def list_services(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if current_user.role == "admin":
        items, total = repository.get_all(db, skip=skip, limit=limit)
    elif current_user.role == "service" and current_user.service_id is not None:
        service = repository.get_by_id(db, current_user.service_id)
        items = [service] if service else []
        total = 1 if service else 0
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado")
    return Page(items=items, total=total, skip=skip, limit=limit, has_next=skip + limit < total)


@router.get("/{service_id}", response_model=ServiceResponse)
def get_service(service_id: int, db: Session = Depends(get_db)):
    service = repository.get_by_id(db, service_id)
    if not service:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Serviço não encontrado")
    return service


@router.post("/", response_model=ServiceResponse, status_code=status.HTTP_201_CREATED)
def create_service(data: ServiceCreate, db: Session = Depends(get_db)):
    if repository.get_by_name(db, data.name):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Já existe um serviço com este nome",
        )
    if get_user_by_email(db, data.user_email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Já existe um usuário com este e-mail",
        )

    service = repository.create(db, data)
    reset_token = create_reset_token(data.user_email)
    reset_link = f"{settings.FRONTEND_URL.rstrip('/')}/reset-password?token={reset_token}"
    body = build_welcome_body(reset_link, data.user_name)

    try:
        send_email(data.user_email, "Bem-vindo ao NEPS", body)
    except EmailDeliveryError:
        # Falha no envio de e-mail não deve impedir criação do serviço em ambiente de teste/dev.
        # Log no módulo de e-mail já ocorreu; aqui tratamos como tentativa "best-effort".
        pass

    return service


@router.patch("/{service_id}", response_model=ServiceResponse)
def update_service(service_id: int, data: ServiceUpdate, db: Session = Depends(get_db)):
    service = repository.get_by_id(db, service_id)
    if not service:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Serviço não encontrado")

    had_user = service.user is not None
    previous_email = service.email

    if data.user_email:
        existing_user = db.query(User).filter(User.email == data.user_email).first()
        if existing_user and existing_user.id != service.user_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Já existe um usuário com este e-mail",
            )

    service = repository.update(db, service_id, data)
    if not service:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Serviço não encontrado")

    should_send_reset = (
        data.user_email is not None and (
            not had_user or previous_email != data.user_email
        )
    )
    if should_send_reset:
        reset_token = create_reset_token(data.user_email)
        reset_link = f"{settings.FRONTEND_URL.rstrip('/')}/reset-password?token={reset_token}"
        body = build_password_reset_body(reset_link)
        try:
            send_email(data.user_email, "Redefinição de senha", body)
        except EmailDeliveryError as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=str(exc),
            )

    return service


@router.put("/{service_id}", response_model=ServiceResponse)
def replace_service(service_id: int, data: ServiceCreate, db: Session = Depends(get_db)):
    service = repository.get_by_id(db, service_id)
    if not service:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Serviço não encontrado")

    had_user = service.user is not None
    previous_email = service.email

    if data.user_email and get_user_by_email(db, data.user_email):
        existing_user = db.query(User).filter(User.email == data.user_email).first()
        if existing_user and existing_user.id != service.user_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Já existe um usuário com este e-mail",
            )
    service.name = data.name
    service.region_id = data.region_id
    service.is_active = data.is_active

    if data.user_email and not service.user:
        temp_password = secrets.token_urlsafe(16)
        user = User(
            name=data.user_name or data.name,
            email=data.user_email,
            password=hash_password(temp_password),
            role="service",
            service_id=service.id,
            is_active=True,
        )
        db.add(user)
        service.user = user
    elif service.user:
        if data.user_name is not None:
            service.user.name = data.user_name
        if data.user_email is not None:
            service.user.email = data.user_email

    db.commit()
    db.refresh(service)

    should_send_reset = (
        data.user_email is not None and (
            not had_user or previous_email != data.user_email
        )
    )
    if should_send_reset:
        reset_token = create_reset_token(data.user_email)
        reset_link = f"{settings.FRONTEND_URL.rstrip('/')}/reset-password?token={reset_token}"
        body = build_password_reset_body(reset_link)
        try:
            send_email(data.user_email, "Redefinição de senha", body)
        except EmailDeliveryError as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=str(exc),
            )

    return service
