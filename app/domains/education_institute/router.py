import math

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.schemas import FilterInfo, Page, PaginationInfo
from app.core.email import EmailDeliveryError, build_welcome_body, send_email
from app.core.jwt import create_reset_token
from app.core.settings import settings
from app.domains.education_institute import repository
from app.domains.education_institute.schemas import (
    EducationInstituteCreate,
    EducationInstituteResponse,
    EducationInstituteUpdate,
)

router = APIRouter(prefix="/education-institutes", tags=["Education Institutes"])

AVAILABLE_FILTERS = ["name_like", "cnpj", "is_active", "priority"]


@router.get("/", response_model=Page[EducationInstituteResponse])
def list_institutes(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    name_like: str | None = Query(None),
    cnpj: str | None = Query(None),
    is_active: bool | None = Query(None),
    priority: int | None = Query(None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    filters = {k: v for k, v in {"name_like": name_like, "cnpj": cnpj, "is_active": is_active, "priority": priority}.items() if v is not None}

    if current_user.role == "admin":
        items, total = repository.get_all(db, page=page, per_page=per_page, filters=filters)
    elif current_user.role == "education_institute" and current_user.education_institute_id is not None:
        institute = repository.get_by_id(db, current_user.education_institute_id)
        if institute:
            items = [institute]
            total = 1
        else:
            items = []
            total = 0
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


@router.get("/{institute_id}", response_model=EducationInstituteResponse)
def get_institute(institute_id: int, db: Session = Depends(get_db)):
    institute = repository.get_by_id(db, institute_id)
    if not institute:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Instituição não encontrada")
    return institute


@router.post("/", response_model=EducationInstituteResponse, status_code=status.HTTP_201_CREATED)
def create_institute(data: EducationInstituteCreate, db: Session = Depends(get_db)):
    institute = repository.create(db, data)
    target_email = data.user_email or data.email

    if target_email:
        reset_token = create_reset_token(target_email)
        reset_link = f"{settings.FRONTEND_URL.rstrip('/')}/reset-password?token={reset_token}"
        body = build_welcome_body(reset_link, data.user_name or institute.name)

        try:
            send_email(target_email, "Bem-vindo ao NEPS", body)
        except EmailDeliveryError:
            pass

    return institute


@router.patch("/{institute_id}", response_model=EducationInstituteResponse)
def update_institute(
    institute_id: int, data: EducationInstituteUpdate, db: Session = Depends(get_db)
):
    institute = repository.update(db, institute_id, data)
    if not institute:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Instituição não encontrada")
    return institute


@router.put("/{institute_id}", response_model=EducationInstituteResponse)
def replace_institute(
    institute_id: int, data: EducationInstituteUpdate, db: Session = Depends(get_db)
):
    return update_institute(institute_id=institute_id, data=data, db=db)