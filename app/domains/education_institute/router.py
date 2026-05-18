from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.schemas import Page
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
legacy_router = APIRouter(prefix="/cadastros/institutions", tags=["Education Institutes (legacy)"])


@router.get("/", response_model=Page[EducationInstituteResponse])
def list_institutes(
    skip: int = 0,
    limit: int = 100,
    is_active: bool | None = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if current_user.role == "admin":
        items, total = repository.get_all(db, skip=skip, limit=limit, is_active=is_active)
    elif current_user.role == "education_institute" and current_user.education_institute_id is not None:
        institute = repository.get_by_id(db, current_user.education_institute_id)
        if institute and (is_active is None or institute.is_active == is_active):
            items = [institute]
            total = 1
        else:
            items = []
            total = 0
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado")
    return Page(items=items, total=total, skip=skip, limit=limit, has_next=skip + limit < total)


@legacy_router.get("/", response_model=Page[EducationInstituteResponse])
def legacy_list_institutes(
    skip: int = 0,
    limit: int = 100,
    is_active: bool | None = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return list_institutes(skip=skip, limit=limit, is_active=is_active, db=db, current_user=current_user)


@router.get("/{institute_id}", response_model=EducationInstituteResponse)
def get_institute(institute_id: int, db: Session = Depends(get_db)):
    institute = repository.get_by_id(db, institute_id)
    if not institute:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Instituição não encontrada")
    return institute


@legacy_router.get("/{institute_id}", response_model=EducationInstituteResponse)
def legacy_get_institute(institute_id: int, db: Session = Depends(get_db)):
    return get_institute(institute_id=institute_id, db=db)


@router.post("/", response_model=EducationInstituteResponse, status_code=status.HTTP_201_CREATED)
def create_institute(data: EducationInstituteCreate, db: Session = Depends(get_db)):
    institute = repository.create(db, data)
    target_email = data.user_email or data.email
    
    # Send welcome email if user was created
    if target_email:
        reset_token = create_reset_token(target_email)
        reset_link = f"{settings.FRONTEND_URL.rstrip('/')}/reset-password?token={reset_token}"
        body = build_welcome_body(reset_link, data.user_name or institute.name)
        
        try:
            send_email(target_email, "Bem-vindo ao NEPS", body)
        except EmailDeliveryError:
            # Email delivery failure doesn't prevent institute creation in dev/test
            pass
    
    return institute


@legacy_router.post("/", response_model=EducationInstituteResponse, status_code=status.HTTP_201_CREATED)
def legacy_create_institute(data: EducationInstituteCreate, db: Session = Depends(get_db)):
    return create_institute(data=data, db=db)


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


@legacy_router.patch("/{institute_id}", response_model=EducationInstituteResponse)
def legacy_update_institute(
    institute_id: int, data: EducationInstituteUpdate, db: Session = Depends(get_db)
):
    return update_institute(institute_id=institute_id, data=data, db=db)


@legacy_router.put("/{institute_id}", response_model=EducationInstituteResponse)
def legacy_replace_institute(
    institute_id: int, data: EducationInstituteUpdate, db: Session = Depends(get_db)
):
    return update_institute(institute_id=institute_id, data=data, db=db)
