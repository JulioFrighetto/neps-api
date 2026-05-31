import math

from fastapi import APIRouter, Body, Depends, HTTPException, status
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
from app.core.schemas import FilterInfo, Page, PaginationInfo
from app.core.settings import settings
from app.domains.service import repository
from app.domains.service.schemas import ServiceCreate, ServiceResponse, ServiceUpdate
from app.domains.user.model import User
from app.domains.user.repository import get_by_email as get_user_by_email
from app.core.security import hash_password
import secrets
from pydantic import BaseModel

router = APIRouter(prefix="/services", tags=["Campos de Estágio"])

AVAILABLE_FILTERS = ["name_like", "region_id", "is_active"]


class ServiceGetRequest(BaseModel):
    service_id: int


class ServiceUpdateRequest(ServiceUpdate):
    service_id: int


class ServiceReplaceRequest(ServiceCreate):
    service_id: int


@router.get("/", response_model=Page[ServiceResponse])
def list_services(
    page: int = Body(1, ge=1),
    per_page: int = Body(10, ge=1, le=100),
    name_like: str | None = Body(None),
    region_id: int | None = Body(None),
    is_active: bool | None = Body(None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    filters = {k: v for k, v in {"name_like": name_like, "region_id": region_id, "is_active": is_active}.items() if v is not None}

    if current_user.role == "admin":
        items, total = repository.get_all(db, page=page, per_page=per_page, filters=filters)
    elif current_user.role == "service" and current_user.service_id is not None:
        service = repository.get_by_id(db, current_user.service_id)
        items = [service] if service else []
        total = 1 if service else 0
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado")
    return Page(
        items=items,
        pagination=PaginationInfo(
            page=page,
            per_page=per_page,
            total=total,
            total_pages=max(1, math.ceil(total / per_page)) if total > 0 else 0,
        ),
        filters=FilterInfo(applied=list(filters.keys()), available=AVAILABLE_FILTERS),
    )


@router.post("/detail", response_model=ServiceResponse)
def get_service(data: ServiceGetRequest, db: Session = Depends(get_db)):
    service = repository.get_by_id(db, data.service_id)
    if not service:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campo de estágio não encontrado")
    return service


@router.post("/", response_model=ServiceResponse, status_code=status.HTTP_201_CREATED)
def create_service(data: ServiceCreate, db: Session = Depends(get_db)):
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

    service = repository.create(db, data)
    if data.user_email:
        reset_token = create_reset_token(data.user_email)
        reset_link = f"{settings.FRONTEND_URL.rstrip('/')}/reset-password?token={reset_token}"
        body = build_welcome_body(reset_link, data.user_name or data.name)

        try:
            send_email(data.user_email, "Bem-vindo ao NEPS", body)
        except EmailDeliveryError:
            # Falha no envio de e-mail não deve impedir criação do serviço em ambiente de teste/dev.
            # Log no módulo de e-mail já ocorreu; aqui tratamos como tentativa "best-effort".
            pass

    return service


@router.patch("/", response_model=ServiceResponse)
def update_service(data: ServiceUpdateRequest, db: Session = Depends(get_db)):
    service = repository.get_by_id(db, data.service_id)
    if not service:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campo de estágio não encontrado")

    if data.user_email:
        existing_user = db.query(User).filter(User.email == data.user_email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Já existe um usuário com este e-mail",
            )

    service = repository.update(db, data.service_id, data)
    if not service:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campo de estágio não encontrado")

    if data.user_email:
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


@router.put("/", response_model=ServiceResponse)
def replace_service(data: ServiceReplaceRequest, db: Session = Depends(get_db)):
    service = repository.get_by_id(db, data.service_id)
    if not service:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campo de estágio não encontrado")

    if data.user_email and get_user_by_email(db, data.user_email):
        existing_user = db.query(User).filter(User.email == data.user_email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Já existe um usuário com este e-mail",
            )
    service.name = data.name
    service.region_id = data.region_id
    service.is_active = data.is_active

    if data.user_email:
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

    db.commit()

    if data.user_email:
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

    return repository.get_by_id(db, data.service_id) or service
