import math

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.schemas import FilterInfo, Page, PaginationInfo
from app.domains.period import repository
from app.domains.period.schemas import PeriodCreate, PeriodResponse, PeriodUpdate

router = APIRouter(prefix="/periods", tags=["Periods"])

AVAILABLE_FILTERS = ["name_like", "is_active", "start_date_from", "start_date_to", "end_date_from", "end_date_to"]


@router.get("/", response_model=Page[PeriodResponse])
def list_periods(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    name_like: str | None = Query(None),
    is_active: bool | None = Query(None),
    start_date_from: str | None = Query(None),
    start_date_to: str | None = Query(None),
    end_date_from: str | None = Query(None),
    end_date_to: str | None = Query(None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    filters = {k: v for k, v in {
        "name_like": name_like,
        "is_active": is_active,
        "start_date_from": start_date_from,
        "start_date_to": start_date_to,
        "end_date_from": end_date_from,
        "end_date_to": end_date_to,
    }.items() if v is not None}

    institute_priority = None
    if current_user.role == "education_institute":
        if current_user.education_institute_id is None or current_user.education_institute is None:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado")
        institute_priority = current_user.education_institute.priority
    elif current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado")

    items, total = repository.get_all(
        db,
        page=page,
        per_page=per_page,
        filters=filters,
        institute_priority=institute_priority,
    )
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


@router.get("/{period_id}", response_model=PeriodResponse)
def get_period(period_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    institute_priority = None
    if current_user.role == "education_institute":
        if current_user.education_institute_id is None or current_user.education_institute is None:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado")
        institute_priority = current_user.education_institute.priority
    elif current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado")

    period = repository.get_by_id(db, period_id, institute_priority=institute_priority)
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