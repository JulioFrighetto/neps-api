from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.schemas import Page
from app.domains.discipline import repository
from app.domains.discipline.schemas import (DisciplineBrief, DisciplineCreate,
                                            DisciplineFilters,
                                            DisciplineGetRequest,
                                            DisciplineResponse,
                                            DisciplineUpdate,
                                            DisciplineUpdateRequest)
from app.domains.discipline.usecases.create import create_usecase
from app.domains.discipline.usecases.find_one import find_one_usecase
from app.domains.discipline.usecases.get_all import get_all_usecase
from app.domains.discipline.usecases.update import update_usecase

router = APIRouter(prefix="/disciplines", tags=["Disciplines"])


def _require_not_internships(current_user):
    if current_user.role == "internships":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado")


@router.get("/list", response_model=Page[DisciplineBrief])
def list_disciplines_brief(
    filters: DisciplineFilters = Depends(),
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    _require_not_internships(current_user)
    page_obj = get_all_usecase(
        db=db,
        page=page,
        per_page=per_page,
        filters=filters.model_dump(exclude_none=True),
    )
    brief_items = [{"id": d.id, "name": d.name} for d in page_obj.items]
    return Page(
        items=brief_items,
        pagination=page_obj.pagination,
        filters=page_obj.filters,
    )


@router.get("/", response_model=Page[DisciplineResponse])
def list_disciplines(
    filters: DisciplineFilters = Depends(),
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    _require_not_internships(current_user)
    return get_all_usecase(
        db=db,
        page=page,
        per_page=per_page,
        filters=filters.model_dump(exclude_none=True),
    )


@router.post("/detail", response_model=DisciplineResponse)
def get_discipline(data: DisciplineGetRequest, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    _require_not_internships(current_user)
    discipline = find_one_usecase(db, data.discipline_id)
    if not discipline:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Disciplina não encontrada")
    return discipline


@router.post("/", response_model=DisciplineResponse, status_code=status.HTTP_201_CREATED)
def create_discipline(data: DisciplineCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if current_user.role not in ("admin", "education_institute"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado")
    return create_usecase(db, data)


@router.put("/", response_model=DisciplineResponse)
@router.patch("/", response_model=DisciplineResponse)
def update_discipline(data: DisciplineUpdateRequest, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if current_user.role not in ("admin", "education_institute"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado")
    discipline = update_usecase(db, data)
    if not discipline:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Disciplina não encontrada")
    return discipline
