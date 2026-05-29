from datetime import date

from sqlalchemy.orm import Session, selectinload

from app.domains.history.model import History


def get_by_period(db: Session, period_id: int, page: int = 1, per_page: int = 10) -> tuple[list[History], int]:
    query = (
        db.query(History)
        .options(selectinload(History.student), selectinload(History.period))
        .filter(History.period_id == period_id)
        .order_by(History.start_date.desc(), History.id.desc())
    )
    total = query.count()
    items = query.offset((page - 1) * per_page).limit(per_page).all()
    return items, total


def get_by_room(db: Session, room_id: int, page: int = 1, per_page: int = 10) -> tuple[list[History], int]:
    query = (
        db.query(History)
        .options(
            selectinload(History.student),
            selectinload(History.period),
            selectinload(History.room),
            selectinload(History.schedule),
        )
        .filter(History.room_id == room_id)
        .order_by(History.start_date.desc(), History.id.desc())
    )
    total = query.count()
    items = query.offset((page - 1) * per_page).limit(per_page).all()
    return items, total


def get_by_schedule(db: Session, schedule_id: int, page: int = 1, per_page: int = 10) -> tuple[list[History], int]:
    query = (
        db.query(History)
        .options(
            selectinload(History.student),
            selectinload(History.period),
            selectinload(History.room),
            selectinload(History.schedule),
        )
        .filter(History.schedule_id == schedule_id)
        .order_by(History.start_date.desc(), History.id.desc())
    )
    total = query.count()
    items = query.offset((page - 1) * per_page).limit(per_page).all()
    return items, total


def resolve_room_id_for_student(db: Session, student_id: int) -> int | None:
    from app.domains.room_schedule.models_nested import Schedule, ScheduleDay, SchedulePeriod, schedule_period_students

    row = (
        db.query(Schedule.room_id)
        .join(ScheduleDay, ScheduleDay.schedule_id == Schedule.id)
        .join(SchedulePeriod, SchedulePeriod.schedule_day_id == ScheduleDay.id)
        .join(schedule_period_students, schedule_period_students.c.schedule_period_id == SchedulePeriod.id)
        .filter(schedule_period_students.c.student_id == student_id)
        .order_by(Schedule.room_id.asc())
        .first()
    )
    return row[0] if row else None


def resolve_schedule_id_for_student(db: Session, student_id: int) -> int | None:
    from app.domains.room_schedule.models_nested import Schedule, ScheduleDay, SchedulePeriod, schedule_period_students

    row = (
        db.query(Schedule.id)
        .join(ScheduleDay, ScheduleDay.schedule_id == Schedule.id)
        .join(SchedulePeriod, SchedulePeriod.schedule_day_id == ScheduleDay.id)
        .join(schedule_period_students, schedule_period_students.c.schedule_period_id == SchedulePeriod.id)
        .filter(schedule_period_students.c.student_id == student_id)
        .order_by(Schedule.id.asc())
        .first()
    )
    return row[0] if row else None


def create_link_history(
    db: Session,
    period_id: int,
    student_id: int,
    schedule_id: int | None = None,
    room_id: int | None = None,
    start_date: date | None = None,
) -> History:
    history = History(
        period_id=period_id,
        student_id=student_id,
        schedule_id=schedule_id,
        room_id=room_id,
        start_date=start_date or date.today(),
    )
    db.add(history)
    return history


def close_active_history(
    db: Session,
    period_id: int,
    student_id: int,
    end_date: date | None = None,
) -> History | None:
    history = (
        db.query(History)
        .filter(
            History.period_id == period_id,
            History.student_id == student_id,
            History.end_date.is_(None),
        )
        .order_by(History.id.desc())
        .first()
    )
    if not history:
        return None

    history.end_date = end_date or date.today()
    return history
