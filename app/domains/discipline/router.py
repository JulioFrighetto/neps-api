from fastapi import APIRouter, Depends, HTTPException, Body, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.schemas import  Page
from app.domains.discipline import repository
from app.domains.discipline.schemas import DisciplineCreate, DisciplineFilters, DisciplineGetRequest, DisciplineResponse, DisciplineUpdate, DisciplineUpdateRequest


from app.domains.discipline.usecases.create import create_usecase
from app.domains.discipline.usecases.find_one import find_one_usecase
from app.domains.discipline.usecases.get_all import get_all_usecase
from app.domains.discipline.usecases.update import update_usecase

router = APIRouter(prefix="/disciplines", tags=["Disciplines"])

@router.get("/", response_model=Page[DisciplineResponse])
def list_disciplines(
    filters: DisciplineFilters = Body(default_factory=DisciplineFilters),
    page: int = Body(1, ge=1),
    per_page: int = Body(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return get_all_usecase(
        db=db,
        page=page,
        per_page=per_page,
        filters=filters.model_dump(exclude_none=True),
    )


@router.post("/detail", response_model=DisciplineResponse)
def get_discipline(data: DisciplineGetRequest, db: Session = Depends(get_db)):
    discipline = find_one_usecase(db, data.discipline_id)
    if not discipline:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Curso não encontrado")
    return discipline


@router.post("/", response_model=DisciplineResponse, status_code=status.HTTP_201_CREATED)
def create_discipline(data: DisciplineCreate, db: Session = Depends(get_db)):
    return create_usecase(db, data)


@router.put("/", response_model=DisciplineResponse)
@router.patch("/", response_model=DisciplineResponse)
def update_discipline(data: DisciplineUpdateRequest, db: Session = Depends(get_db)):
    discipline = update_usecase(db, data.discipline_id, data)
    if not discipline:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Curso não encontrado")
    return discipline
