from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.schemas import Page
from app.domains.period import repository
from app.domains.period.schemas import PeriodCreate, PeriodResponse, PeriodUpdate

router = APIRouter(prefix="/periods", tags=["Periods"])


@router.get("/", response_model=Page[PeriodResponse])
def list_periods(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    items, total = repository.get_all(db, skip=skip, limit=limit)
    return Page(items=items, total=total, skip=skip, limit=limit, has_next=skip + limit < total)


@router.get("/{period_id}", response_model=PeriodResponse)
def get_period(period_id: int, db: Session = Depends(get_db)):
    period = repository.get_by_id(db, period_id)
    if not period:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Período não encontrado")
    return period


@router.post("/", response_model=PeriodResponse, status_code=status.HTTP_201_CREATED)
def create_period(data: PeriodCreate, db: Session = Depends(get_db)):
    return repository.create(db, data)


@router.patch("/{period_id}", response_model=PeriodResponse)
def update_period(period_id: int, data: PeriodUpdate, db: Session = Depends(get_db)):
    period = repository.update(db, period_id, data)
    if not period:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Período não encontrado")
    return period