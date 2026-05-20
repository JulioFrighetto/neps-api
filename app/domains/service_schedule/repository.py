from sqlalchemy.orm import Session

from app.domains.service_room.model import ServiceRoom
from app.domains.service_schedule.model import ServiceSchedule
from app.domains.service_schedule.schemas import ServiceScheduleCreate, ServiceScheduleUpdate


def get_all(db: Session, skip: int = 0, limit: int = 100) -> tuple[list[ServiceSchedule], int]:
    query = db.query(ServiceSchedule)
    total = query.count()
    items = query.offset(skip).limit(limit).all()
    return items, total


def get_by_service(db: Session, service_id: int, skip: int = 0, limit: int = 100) -> tuple[list[ServiceSchedule], int]:
    query = (
        db.query(ServiceSchedule)
        .join(ServiceRoom, ServiceSchedule.service_room_id == ServiceRoom.id)
        .filter(ServiceRoom.service_id == service_id)
    )
    total = query.count()
    items = query.offset(skip).limit(limit).all()
    return items, total


def get_by_id(db: Session, service_schedule_id: int) -> ServiceSchedule | None:
    return db.query(ServiceSchedule).filter(ServiceSchedule.id == service_schedule_id).first()


def get_by_room(db: Session, service_room_id: int) -> list[ServiceSchedule]:
    return db.query(ServiceSchedule).filter(ServiceSchedule.service_room_id == service_room_id).all()


def get_by_room_and_day(db: Session, service_room_id: int, week_day: str) -> list[ServiceSchedule]:
    return (
        db.query(ServiceSchedule)
        .filter(ServiceSchedule.service_room_id == service_room_id)
        .filter(ServiceSchedule.week_day == week_day)
        .all()
    )


def get_by_slot(
    db: Session, service_room_id: int, week_day: str, shift: str
) -> ServiceSchedule | None:
    return (
        db.query(ServiceSchedule)
        .filter(ServiceSchedule.service_room_id == service_room_id)
        .filter(ServiceSchedule.week_day == week_day)
        .filter(ServiceSchedule.shift == shift)
        .first()
    )


def create(db: Session, data: ServiceScheduleCreate) -> ServiceSchedule:
    schedule = ServiceSchedule(**data.model_dump())
    db.add(schedule)
    db.commit()
    db.refresh(schedule)
    return schedule


def update(
    db: Session, service_schedule_id: int, data: ServiceScheduleUpdate
) -> ServiceSchedule | None:
    schedule = get_by_id(db, service_schedule_id)
    if not schedule:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(schedule, field, value)
    db.commit()
    db.refresh(schedule)
    return schedule


def delete(db: Session, service_schedule_id: int) -> bool:
    schedule = get_by_id(db, service_schedule_id)
    if not schedule:
        return False
    db.delete(schedule)
    db.commit()
    return True
