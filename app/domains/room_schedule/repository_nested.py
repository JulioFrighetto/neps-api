from sqlalchemy.orm import Session, selectinload

from app.domains.room.model import Room
from app.domains.room.repository import get_by_id as get_room_by_id
from app.domains.room_schedule.models_nested import Schedule, ScheduleDay, SchedulePeriod
from app.domains.student.model import Student

DAYS_OF_WEEK = ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY", "SUNDAY"]
PERIODS = ["MORNING", "AFTERNOON", "EVENING"]


def create_schedule_for_room(db: Session, room_id: int) -> Schedule:
    existing = get_schedule_by_room(db, room_id)
    if existing:
        return existing

    schedule = Schedule(room_id=room_id)
    db.add(schedule)
    db.flush()

    for day_name in DAYS_OF_WEEK:
        day = ScheduleDay(schedule_id=schedule.id, day_of_week=day_name)
        db.add(day)
        db.flush()

        for period_name in PERIODS:
            db.add(
                SchedulePeriod(
                    schedule_day_id=day.id,
                    period=period_name,
                )
            )

    db.commit()
    return get_schedule_by_room(db, room_id) or schedule


def get_schedule_by_room(db: Session, room_id: int) -> Schedule | None:
    return (
        db.query(Schedule)
        .options(
            selectinload(Schedule.days).selectinload(ScheduleDay.periods).selectinload(SchedulePeriod.students)
        )
        .filter(Schedule.room_id == room_id)
        .first()
    )


def get_by_id(db: Session, schedule_id: int) -> Schedule | None:
    return (
        db.query(Schedule)
        .options(
            selectinload(Schedule.days).selectinload(ScheduleDay.periods).selectinload(SchedulePeriod.students)
        )
        .filter(Schedule.id == schedule_id)
        .first()
    )


def get_period_for_room(db: Session, room_id: int, day_of_week: str, period_name: str) -> SchedulePeriod | None:
    schedule = get_schedule_by_room(db, room_id)
    if not schedule:
        return None

    for day in schedule.days:
        if day.day_of_week == day_of_week:
            for period in day.periods:
                if period.period == period_name:
                    return period
    return None


def assign_student_to_period(
    db: Session,
    room_id: int,
    day_of_week: str,
    period_name: str,
    student_id: int,
) -> SchedulePeriod | None:
    room: Room | None = get_room_by_id(db, room_id)
    if not room:
        return None

    period = get_period_for_room(db, room_id, day_of_week, period_name)
    if not period:
        return None

    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        return None

    if any(existing.id == student_id for existing in period.students):
        raise ValueError("Aluno já está vinculado a este horário")

    if len(period.students) >= room.room_capacity:
        raise ValueError("Período lotado")

    period.students.append(student)
    db.commit()
    db.refresh(period)
    return get_period_for_room(db, room_id, day_of_week, period_name)


def remove_student_from_period(
    db: Session,
    room_id: int,
    day_of_week: str,
    period_name: str,
    student_id: int,
) -> SchedulePeriod | None:
    period = get_period_for_room(db, room_id, day_of_week, period_name)
    if not period:
        return None

    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        return None

    if not any(existing.id == student_id for existing in period.students):
        return None

    period.students.remove(student)
    db.commit()
    db.refresh(period)
    return get_period_for_room(db, room_id, day_of_week, period_name)
