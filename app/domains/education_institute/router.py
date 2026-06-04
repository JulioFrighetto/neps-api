import math

from fastapi import APIRouter, Depends, HTTPException, Body, status
from pydantic import BaseModel
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
from app.domains.education_institute.usecases import find_one
from app.domains.education_institute.usecases.create import create_usecase
from app.domains.education_institute.usecases.get_all import get_all_usecase
from app.domains.education_institute.usecases.update import update_usecase
from app.domains.education_institute.usecases.update import update_usecase

router = APIRouter(prefix="/education-institutes", tags=["Education Institutes"])

AVAILABLE_FILTERS = ["name_like", "cnpj", "is_active", "priority"]


class InstituteGetRequest(BaseModel):
    institute_id: int


class InstituteUpdateRequest(EducationInstituteUpdate):
    institute_id: int


@router.get("/", response_model=Page[EducationInstituteResponse])
def list_institutes(
    page: int = Body(1, ge=1),
    per_page: int = Body(10, ge=1, le=100),
    name_like: str | None = Body(None),
    cnpj: str | None = Body(None),
    is_active: bool | None = Body(None),
    priority: int | None = Body(None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    filters = {k: v for k, v in {"name_like": name_like, "cnpj": cnpj, "is_active": is_active, "priority": priority}.items() if v is not None}
    return get_all_usecase(
        db=db,
        page=page,
        per_page=per_page,
        filters=filters,
        current_user=current_user,
        )


@router.post("/detail", response_model=EducationInstituteResponse)
def get_institute(data: InstituteGetRequest, db: Session = Depends(get_db)):
    institute = find_one.find_one_usecase(db, data.institute_id)
    if not institute:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Instituição não encontrada")
    return institute


@router.post("/", response_model=EducationInstituteResponse, status_code=status.HTTP_201_CREATED)
def create_institute(data: EducationInstituteCreate, db: Session = Depends(get_db)):
    institute = create_usecase(db, data)
    return institute


@router.patch("/", response_model=EducationInstituteResponse)
def update_institute(data: InstituteUpdateRequest, db: Session = Depends(get_db)):
    institute = update_usecase(db, data.institute_id, data)
    if not institute:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Instituição não encontrada")
    return institute


@router.put("/", response_model=EducationInstituteResponse)
def replace_institute(data: InstituteUpdateRequest, db: Session = Depends(get_db)):
    institute = update_usecase(db, data.institute_id, data)
    if not institute:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Instituição não encontrada")
    return institute