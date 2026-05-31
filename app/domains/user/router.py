import math

from fastapi import APIRouter, Body, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.email import EmailDeliveryError, build_welcome_body, send_email
from app.core.deps import get_current_admin_user, get_current_user
from app.core.jwt import create_reset_token
from app.core.schemas import FilterInfo, Page, PaginationInfo
from app.core.settings import settings
from app.domains.education_institute.repository import get_by_id as get_institute_by_id
from app.domains.service.repository import get_by_id as get_service_by_id
from app.domains.user import repository
from app.domains.user.schemas import (
    UserChangePassword,
    UserCreate,
    UserResponse,
    UserUpdate,
)
from app.core.security import hash_password
from pydantic import BaseModel

router = APIRouter(prefix="/users", tags=["Users"])


class RoleItem(BaseModel):
    label: str
    value: str


class RolesResponse(BaseModel):
    items: list[RoleItem]


class UserGetRequest(BaseModel):
    user_id: int


class UserUpdateRequest(UserUpdate):
    user_id: int


class UserReplaceRequest(UserCreate):
    user_id: int


class UserChangePasswordRequest(UserChangePassword):
    user_id: int

AVAILABLE_FILTERS = ["name_like", "email_like", "role", "role_in", "is_active"]


@router.get("/me", response_model=UserResponse)
def me(current_user=Depends(get_current_user)):
    return current_user


@router.get("/", response_model=Page[UserResponse])
def list_users(
    page: int = Body(1, ge=1),
    per_page: int = Body(10, ge=1, le=100),
    name: str | None = Body(None),
    name_like: str | None = Body(None),
    email_like: str | None = Body(None),
    role: str | None = Body(None),
    role_in: str | None = Body(None),
    is_active: bool | None = Body(None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin_user),
):
    filters = {k: v for k, v in {
        "name_like": name if name is not None else name_like,
        "email_like": email_like,
        "role": role,
        "role_in": role_in,
        "is_active": is_active,
    }.items() if v is not None}
    items, total = repository.get_all(db, page=page, per_page=per_page, filters=filters)
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


@router.get("/roles", response_model=RolesResponse)
def list_roles():
    return RolesResponse(items=[
        RoleItem(label="Administrador", value="admin"),
        RoleItem(label="Instituição de Ensino", value="education_institute"),
        RoleItem(label="Campo de Estágio", value="service"),
    ])


@router.post("/detail", response_model=UserResponse)
def get_user(
    data: UserGetRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin_user),
):
    user = repository.get_by_id(db, data.user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")
    return user


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    data: UserCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin_user),
):
    if repository.get_by_email(db, data.email):
        raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Já existe um usuário com este e-mail",
            )
    if data.role == "education_institute":
        institute = get_institute_by_id(db, data.education_institute_id)
        if not institute:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Instituição de ensino não encontrada",
            )
    if data.role == "service":
        service = get_service_by_id(db, data.service_id) if data.service_id is not None else None
        if not service:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campo de estágio não encontrado",
            )

    user = repository.create(db, data)
    reset_token = create_reset_token(user.email)
    reset_link = f"{settings.FRONTEND_URL.rstrip('/')}/reset-password?token={reset_token}"
    body = build_welcome_body(reset_link, user.name)

    try:
        send_email(user.email, "Bem-vindo à NEPS API", body)
    except EmailDeliveryError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        )

    return user


@router.patch("/", response_model=UserResponse)
def update_user(
    data: UserUpdateRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    # Admins may update any user (including toggling is_active). Regular users may update only themselves.
    if current_user.role != "admin" and current_user.id != data.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado")
    user = repository.update(db, data.user_id, data)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")
    return user


@router.put("/", response_model=UserResponse)
def replace_user(
    data: UserReplaceRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin_user),
):
    # Admin-only full replace/update of user
    user = repository.get_by_id(db, data.user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")

    # validate linked entities when role requires them
    if data.role == "service":
        service = get_service_by_id(db, data.service_id) if data.service_id is not None else None
        if not service:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campo de estágio não encontrado",
            )
    if data.role == "education_institute":
        institute = get_institute_by_id(db, data.education_institute_id)
        if not institute:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Instituição de ensino não encontrada",
            )

    # ensure email uniqueness
    existing = repository.get_by_email(db, data.email)
    if existing and existing.id != data.user_id:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Já existe um usuário com este e-mail")

    # apply changes (password is NOT updated here — use /change-password endpoint)
    user.name = data.name
    user.email = data.email
    user.role = data.role
    user.service_id = data.service_id
    user.education_institute_id = data.education_institute_id
    user.is_active = data.is_active

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Não foi possível atualizar o usuário devido a vínculo duplicado",
        )
    db.refresh(user)
    return user


@router.post("/change-password", status_code=status.HTTP_204_NO_CONTENT)
def change_password(
    data: UserChangePasswordRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if current_user.id != data.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado")
    updated = repository.change_password(db, data.user_id, data.current_password, data.new_password)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Senha atual incorreta"
        )
