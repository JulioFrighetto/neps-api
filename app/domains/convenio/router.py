from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.schemas import Page
from app.domains.convenio.schemas import (
    ConvenioBrief, ConvenioCreate, ConvenioFilters, ConvenioResponse,
    ConvenioUpdate)
from app.domains.convenio.usecases import find_one
from app.domains.convenio.usecases.create import create_usecase
from app.domains.convenio.usecases.get_all import get_all_usecase
from app.domains.convenio.usecases.update import update_usecase

router = APIRouter(prefix="/convenios", tags=["Convênios"])

class ConvenioGetRequest(BaseModel):
    convenio_id: int

class ConvenioUpdateRequest(ConvenioUpdate):
    convenio_id: int

@router.get("/list", response_model=Page[ConvenioBrief])
def list_convenios_brief(
    filters: ConvenioFilters = Depends(),
    current_user=Depends(get_current_user),
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=500),
    db: Session = Depends(get_db),
):
    page_obj = get_all_usecase(
        db=db,
        page=page,
        per_page=per_page,
        filters=filters.model_dump(exclude_none=True),
    )
    brief_items = [{"id": c.id, "name": c.name, "status": c.status} for c in page_obj.items]
    return Page(
        items=brief_items,
        pagination=page_obj.pagination,
        filters=page_obj.filters,
    )

@router.get("/", response_model=Page[ConvenioResponse])
def list_convenios(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=500),
    name_like: str | None = Query(None),
    cnpj: str | None = Query(None),
    is_active: bool | None = Query(None),
    priority: int | None = Query(None),
    status_filter: str | None = Query(None, alias="status"),
    education_institute_id: int | None = Query(None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    filters = {
        k: v
        for k, v in {
            "name_like": name_like,
            "cnpj": cnpj,
            "is_active": is_active,
            "priority": priority,
            "status": status_filter,
            "education_institute_id": education_institute_id,
        }.items()
        if v is not None
    }
    return get_all_usecase(db=db, page=page, per_page=per_page, filters=filters)

@router.post("/detail", response_model=ConvenioResponse)
def get_convenio(data: ConvenioGetRequest, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    convenio = find_one.find_one_usecase(db, data.convenio_id)
    if not convenio:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Convênio não encontrado")
    return convenio

@router.post("/", response_model=ConvenioResponse, status_code=status.HTTP_201_CREATED)
def create_convenio(data: ConvenioCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return create_usecase(db, data)

@router.patch("/", response_model=ConvenioResponse)
def update_convenio(data: ConvenioUpdateRequest, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    convenio = update_usecase(db, data.convenio_id, data)
    if not convenio:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Convênio não encontrado")
    return convenio

@router.put("/", response_model=ConvenioResponse)
def replace_convenio(data: ConvenioUpdateRequest, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    convenio = update_usecase(db, data.convenio_id, data)
    if not convenio:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Convênio não encontrado")
    return convenio
