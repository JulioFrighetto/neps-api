from sqlalchemy.orm import Session

from app.core.filters import apply_filters
from app.domains.period.model import Period
from app.domains.period.schemas import PeriodCreate, PeriodUpdate


def get_all(db: Session, page: int = 1, per_page: int = 10, filters: dict | None = None) -> tuple[list[Period], int]:
    query = db.query(Period)
    if filters:
        query, _ = apply_filters(query, Period, filters)
    total = query.count()
    items = query.offset((page - 1) * per_page).limit(per_page).all()
    return items, total


def get_by_id(db: Session, period_id: int) -> Period | None:
    return db.query(Period).filter(Period.id == period_id).first()


def create(db: Session, data: PeriodCreate) -> Period:
    period = Period(**data.model_dump())
    db.add(period)
    db.commit()
    db.refresh(period)
    return period


def update(db: Session, period_id: int, data: PeriodUpdate) -> Period | None:
    period = get_by_id(db, period_id)
    if not period:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(period, field, value)
    db.commit()
    db.refresh(period)
    return period


def delete(db: Session, period_id: int) -> bool:
    period = get_by_id(db, period_id)
    if not period:
        return False
    db.delete(period)
    db.commit()
    return True