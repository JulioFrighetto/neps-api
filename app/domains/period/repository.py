from datetime import date

from sqlalchemy import and_, or_
from sqlalchemy.orm import Session, Query, selectinload

from app.core.filters import apply_filters
from app.domains.history import repository as history_repository
from app.domains.period.model import Period
from app.domains.period.schemas import PeriodCreate, PeriodUpdate


def _apply_visibility_filter(query: Query, institute_priority: int | None = None, today: date | None = None) -> Query:
    if today is None:
        today = date.today()

    # Admins (institute_priority is None) see all active periods
    if institute_priority is None:
        return query.filter(Period.is_active.is_(True))

    open_period = and_(Period.start_date <= today, Period.end_date >= today)
    priority_period = and_(Period.priority_start_date <= today, Period.priority_end_date >= today)

    # institute_priority == 0 => prioritized institute: see priority window OR open window
    if institute_priority == 0:
        return query.filter(Period.is_active.is_(True)).filter(or_(open_period, priority_period))

    # non-priority institutes see only open window
    return query.filter(Period.is_active.is_(True)).filter(open_period)


def get_all(
    db: Session,
    page: int = 1,
    per_page: int = 100,
    filters: dict | None = None,
    institute_priority: int | None = None,
    today: date | None = None,
) -> tuple[list[Period], int]:
    query = db.query(Period)

    if filters:
        query, _applied = apply_filters(query, Period, filters)

    query = _apply_visibility_filter(query, institute_priority=institute_priority, today=today)

    total = query.count()
    items = query.offset((page - 1) * per_page).limit(per_page).all()
    return items, total


def get_by_id(
    db: Session,
    period_id: int,
    institute_priority: int | None = None,
    today: date | None = None,
) -> Period | None:
    query = db.query(Period).filter(Period.id == period_id)
    query = _apply_visibility_filter(query, institute_priority=institute_priority, today=today)
    return query.first()


def get_by_id_with_students(
    db: Session,
    period_id: int,
    institute_priority: int | None = None,
    today: date | None = None,
) -> Period | None:
    query = db.query(Period).options(selectinload(Period.students)).filter(Period.id == period_id)
    query = _apply_visibility_filter(query, institute_priority=institute_priority, today=today)
    return query.first()


def link_student(db: Session, period_id: int, student) -> None:
    # `student` should be a Student instance
    period = db.query(Period).filter(Period.id == period_id).first()
    if not period:
        raise ValueError("Period not found")
    if any(s.id == student.id for s in period.students):
        raise ValueError("Student already linked")
    period.students.append(student)
    schedule_id = history_repository.resolve_schedule_id_for_student(db, student.id)
    room_id = history_repository.resolve_room_id_for_student(db, student.id)
    history_repository.create_or_update_link_history(
        db,
        period_id,
        student.id,
        schedule_id=schedule_id,
        room_id=room_id,
    )
    db.commit()


def unlink_student(db: Session, period_id: int, student) -> None:
    period = db.query(Period).filter(Period.id == period_id).first()
    if not period:
        raise ValueError("Period not found")
    if not any(s.id == student.id for s in period.students):
        raise ValueError("Student not linked")
    period.students.remove(student)
    history_repository.close_active_history(db, period_id, student.id)
    db.commit()


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