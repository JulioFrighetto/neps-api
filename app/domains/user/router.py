from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.email import EmailDeliveryError, build_welcome_body, send_email
from app.core.deps import get_current_admin_user, get_current_user
from app.core.jwt import create_reset_token
from app.core.schemas import Page
from app.core.settings import settings
from app.domains.education_institute.repository import get_by_id as get_institute_by_id
from app.domains.internship_field.repository import get_by_id as get_field_by_id
from app.domains.user import repository
from app.domains.user.schemas import (
    UserChangePassword,
    UserCreate,
    UserResponse,
    UserUpdate,
)
from app.core.security import hash_password

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserResponse)
def me(current_user=Depends(get_current_user)):
    return current_user


@router.get("/", response_model=Page[UserResponse])
def list_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin_user),
):
    items, total = repository.get_all(db, skip=skip, limit=limit)
    return Page(items=items, total=total, skip=skip, limit=limit, has_next=skip + limit < total)


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
    elif data.role == "internship_field":
        field = get_field_by_id(db, data.internship_field_id)
        if not field:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Unidade não encontrada",
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
    elif data.role == "internship_field":
        field = get_field_by_id(db, data.internship_field_id)
        if not field:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Unidade não encontrada",
            )

    # ensure email uniqueness
    existing = repository.get_by_email(db, data.email)
    if existing and existing.id != user_id:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Já existe um usuário com este e-mail")

    # apply changes
    user.name = data.name
    user.email = data.email
    if data.password is not None:
        user.password = hash_password(data.password)
    user.role = data.role
    user.service_id = data.service_id
    user.education_institute_id = data.education_institute_id
    user.internship_field_id = data.internship_field_id
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
