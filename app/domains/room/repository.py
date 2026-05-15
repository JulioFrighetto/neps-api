from sqlalchemy.orm import Session

from app.domains.room.model import Room, RoomSchedule, RoomTimeTable
from app.domains.room.schemas import (
    RoomCreate,
    RoomScheduleCreate,
    RoomTimeTableCreate,
    RoomUpdate,
)


def get_all(db: Session, skip: int = 0, limit: int = 100) -> list[Room]:
    return db.query(Room).offset(skip).limit(limit).all()


def get_by_id(db: Session, room_id: int) -> Room | None:
    return db.query(Room).filter(Room.id == room_id).first()


def get_by_internship_field(db: Session, internship_field_id: int) -> list[Room]:
    return db.query(Room).filter(Room.internship_field_id == internship_field_id).all()


def create(db: Session, data: RoomCreate) -> Room:
    room = Room(**data.model_dump())
    db.add(room)
    db.commit()
    db.refresh(room)
    return room


def update(db: Session, room_id: int, data: RoomUpdate) -> Room | None:
    room = get_by_id(db, room_id)
    if not room:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(room, field, value)
    db.commit()
    db.refresh(room)
    return room


def delete(db: Session, room_id: int) -> bool:
    room = get_by_id(db, room_id)
    if not room:
        return False
    db.delete(room)
    db.commit()
    return True


# RoomSchedule
def create_schedule(db: Session, data: RoomScheduleCreate) -> RoomSchedule:
    schedule = RoomSchedule(**data.model_dump())
    db.add(schedule)
    db.commit()
    db.refresh(schedule)
    return schedule


def get_schedules_by_room(db: Session, room_id: int) -> list[RoomSchedule]:
    return db.query(RoomSchedule).filter(RoomSchedule.room_id == room_id).all()


# RoomTimeTable
def create_timetable(db: Session, data: RoomTimeTableCreate) -> RoomTimeTable:
    timetable = RoomTimeTable(**data.model_dump())
    db.add(timetable)
    db.commit()
    db.refresh(timetable)
    return timetable
