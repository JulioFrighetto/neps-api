from sqlalchemy.orm import Session

from app.domains.internships_room.model import InternshipsRoom
from app.domains.internships_schedule.model import InternshipsSchedule
from app.domains.internships_schedule.schemas import InternshipsScheduleCreate, InternshipsScheduleUpdate


def get_all(db: Session, page: int = 1, per_page: int = 10) -> tuple[list[InternshipsSchedule], int]:
    query = db.query(InternshipsSchedule)
    total = query.count()
    items = query.offset((page - 1) * per_page).limit(per_page).all()
    return items, total


def get_by_internships(db: Session, internships_id: int, page: int = 1, per_page: int = 10) -> tuple[list[InternshipsSchedule], int]:
    query = (
        db.query(InternshipsSchedule)
        .join(InternshipsRoom, InternshipsSchedule.internships_room_id == InternshipsRoom.id)
        .filter(InternshipsRoom.internships_id == internships_id)
    )
    total = query.count()
    items = query.offset((page - 1) * per_page).limit(per_page).all()
    return items, total


def get_by_id(db: Session, internships_schedule_id: int) -> InternshipsSchedule | None:
    return db.query(InternshipsSchedule).filter(InternshipsSchedule.id == internships_schedule_id).first()


def get_by_room(db: Session, internships_room_id: int) -> list[InternshipsSchedule]:
    return db.query(InternshipsSchedule).filter(InternshipsSchedule.internships_room_id == internships_room_id).all()


def get_by_room_and_day(db: Session, internships_room_id: int, week_day: str) -> list[InternshipsSchedule]:
    return (
        db.query(InternshipsSchedule)
        .filter(InternshipsSchedule.internships_room_id == internships_room_id)
        .filter(InternshipsSchedule.week_day == week_day)
        .all()
    )


def get_by_slot(
    db: Session, internships_room_id: int, week_day: str, shift: str
) -> InternshipsSchedule | None:
    return (
        db.query(InternshipsSchedule)
        .filter(InternshipsSchedule.internships_room_id == internships_room_id)
        .filter(InternshipsSchedule.week_day == week_day)
        .filter(InternshipsSchedule.shift == shift)
        .first()
    )


def create(db: Session, data: InternshipsScheduleCreate) -> InternshipsSchedule:
    schedule = InternshipsSchedule(**data.model_dump())
    db.add(schedule)
    db.commit()
    db.refresh(schedule)
    return schedule


def update(
    db: Session, internships_schedule_id: int, data: InternshipsScheduleUpdate
) -> InternshipsSchedule | None:
    schedule = get_by_id(db, internships_schedule_id)
    if not schedule:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(schedule, field, value)
    db.commit()
    db.refresh(schedule)
    return schedule


def delete(db: Session, internships_schedule_id: int) -> bool:
    schedule = get_by_id(db, internships_schedule_id)
    if not schedule:
        return False
    db.delete(schedule)
    db.commit()
    return True
