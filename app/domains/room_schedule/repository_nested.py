from datetime import date

from sqlalchemy.orm import Session, selectinload

from app.domains.history import repository as history_repository
from app.domains.room.model import Room
from app.domains.room.repository import get_by_id as get_room_by_id
from app.domains.room_schedule.models_nested import Schedule, ScheduleDay, SchedulePeriod, schedule_period_students
from app.domains.student.model import Student

DAYS_OF_WEEK = ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY", "SUNDAY"]
PERIODS = ["MORNING", "AFTERNOON", "EVENING"]


def _student_has_conflict(
    db: Session,
    student_id: int,
    day_of_week: str,
    period_name: str,
    room_id: int | None = None,
) -> bool:
    query = (
        db.query(SchedulePeriod)
        .join(ScheduleDay, SchedulePeriod.schedule_day_id == ScheduleDay.id)
        .join(Schedule, ScheduleDay.schedule_id == Schedule.id)
        .join(schedule_period_students, schedule_period_students.c.schedule_period_id == SchedulePeriod.id)
        .filter(schedule_period_students.c.student_id == student_id)
        .filter(ScheduleDay.day_of_week == day_of_week)
        .filter(SchedulePeriod.period == period_name)
    )

    if room_id is not None:
        query = query.filter(Schedule.room_id != room_id)

    return db.query(query.exists()).scalar()


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
    period_id: int,
) -> SchedulePeriod | None:
    room: Room | None = get_room_by_id(db, room_id)
    if not room:
        return None

    period = get_period_for_room(db, room_id, day_of_week, period_name)
    if not period:
        return None

    schedule = get_schedule_by_room(db, room_id)
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        return None

    if not student.is_active:
        raise ValueError("Aluno inativo")

    if student.internship_id != room.internships_id:
        raise ValueError("Aluno não está vinculado ao campo de estágio desta sala")

    if student.discipline and student.discipline.requires_gurney and not room.has_gurney:
        raise ValueError("Este aluno requer sala com maca")

    if _student_has_conflict(db, student_id, day_of_week, period_name, room_id=room_id):
        raise ValueError("Aluno já possui horário vinculado em outra sala")

    if any(existing.id == student_id for existing in period.students):
        raise ValueError("Aluno já está vinculado a este horário")

    if len(period.students) >= room.room_capacity:
        raise ValueError("Período lotado")

    period.students.append(student)
    history_repository.create_or_update_link_history(
        db,
        period_id,
        student.id,
        schedule_id=schedule.id if schedule else None,
        room_id=room.id,
        start_date=date.today(),
    )
    db.commit()
    db.refresh(period)
    return get_period_for_room(db, room_id, day_of_week, period_name)


def remove_student_from_period(
    db: Session,
    room_id: int,
    day_of_week: str,
    period_name: str,
    student_id: int,
    period_id: int,
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
    history_repository.close_active_history(db, period_id, student.id, end_date=date.today())
    db.commit()
    db.refresh(period)
    return get_period_for_room(db, room_id, day_of_week, period_name)


def remove_student_from_all_periods(db: Session, student_id: int) -> int:
    result = db.execute(
        schedule_period_students.delete().where(
            schedule_period_students.c.student_id == student_id
        )
    )
    db.commit()
    return result.rowcount or 0


def get_available_slots_for_student(db: Session, student_id: int, room_id: int | None = None) -> list[dict]:
    """Return list of available slots for a student across rooms (or single room if room_id provided).

    Each slot: {"room_id": int, "day_of_week": str, "period": str, "capacity": int, "occupied": int}
    Only returns slots where occupied < capacity (has vacancies).
    """
    from app.domains.room.repository import get_all as get_all_rooms

    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        return []

    rooms = []
    if room_id is not None:
        room = get_room_by_id(db, room_id)
        if room:
            rooms = [room]
    else:
        rooms, _ = get_all_rooms(db, page=1, per_page=10000)

    available = []
    for room in rooms:
        # only rooms belonging to the student's internship field
        if room.internships_id != student.internship_id:
            continue

        # skip rooms that cannot serve this student due to gurney requirement
        if student.discipline and student.discipline.requires_gurney and not room.has_gurney:
            continue

        schedule = create_schedule_for_room(db, room.id)
        for day in schedule.days:
            for period in day.periods:
                # skip if student already in this exact period in any room
                if _student_has_conflict(db, student_id, day.day_of_week, period.period, room_id=None):
                    # if student already assigned to this day+period in some room, not available
                    continue

                # skip if already in this room+period
                if any(s.id == student_id for s in period.students):
                    continue

                occupied = len(period.students)
                capacity = room.room_capacity

                # skip if period is full (no vacancies)
                if occupied >= capacity:
                    continue

                available.append({
                    "id": period.id,
                    "room_id": room.id,
                    "room_name": room.name,
                    "day_of_week": day.day_of_week,
                    "period": period.period,
                    "capacity": capacity,
                    "occupied": occupied,
                })

    return available
