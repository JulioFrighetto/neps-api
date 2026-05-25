import math

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.email import EmailDeliveryError, build_welcome_body, send_email
from app.core.deps import get_current_admin_user, get_current_user
from app.core.jwt import create_reset_token
from app.core.schemas import FilterInfo, Page, PaginationInfo
from app.core.settings import settings
from app.domains.education_institute.repository import get_by_id as get_institute_by_id
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

AVAILABLE_FILTERS = ["name_like", "email_like", "role", "role_in", "is_active"]


@router.get("/me", response_model=UserResponse)
def me(current_user=Depends(get_current_user)):
    return current_user


@router.get("/", response_model=Page[UserResponse])
def list_users(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    name: str | None = Query(None),
    name_like: str | None = Query(None),
    email_like: str | None = Query(None),
    role: str | None = Query(None),
    role_in: str | None = Query(None),
    is_active: bool | None = Query(None),
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
        RoleItem(label="Unidade de Saúde", value="service"),
    ])


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin_user),
):
    user = repository.get_by_id(db, user_id)
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


@router.patch("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    data: UserUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    # Admins may update any user (including toggling is_active). Regular users may update only themselves.
    if current_user.role != "admin" and current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado")
    user = repository.update(db, user_id, data)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")
    return user


@router.put("/{user_id}", response_model=UserResponse)
def replace_user(
    user_id: int,
    data: UserCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin_user),
):
    # Admin-only full replace/update of user
    user = repository.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")

    # validate linked entities when role requires them
    if data.role == "education_institute":
        institute = get_institute_by_id(db, data.education_institute_id)
        if not institute:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Instituição de ensino não encontrada",
            )

    # ensure email uniqueness
    existing = repository.get_by_email(db, data.email)
    if existing and existing.id != user_id:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Já existe um usuário com este e-mail")

    # apply changes (password is NOT updated here — use /change-password endpoint)
    user.name = data.name
    user.email = data.email
    user.role = data.role
    user.service_id = data.service_id
    user.education_institute_id = data.education_institute_id
    user.is_active = data.is_active

    db.commit()
    db.refresh(user)
    return user


@router.post("/{user_id}/change-password", status_code=status.HTTP_204_NO_CONTENT)
def change_password(
    user_id: int,
    data: UserChangePassword,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado")
    updated = repository.change_password(db, user_id, data.current_password, data.new_password)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Senha atual incorreta"
        )
