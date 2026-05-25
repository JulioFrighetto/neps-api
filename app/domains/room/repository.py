from sqlalchemy.orm import Session

from app.core.filters import apply_filters
from app.domains.room.model import Room
from app.domains.room.schemas import (
    RoomCreate,
    RoomUpdate,
)


def get_all(db: Session, page: int = 1, per_page: int = 10, filters: dict | None = None) -> tuple[list[Room], int]:
    query = db.query(Room)
    if filters:
        query, _ = apply_filters(query, Room, filters)
    total = query.count()
    items = query.offset((page - 1) * per_page).limit(per_page).all()
    return items, total


def get_by_id(db: Session, room_id: int) -> Room | None:
    return db.query(Room).filter(Room.id == room_id).first()


def get_by_service(db: Session, service_id: int, page: int = 1, per_page: int = 10, filters: dict | None = None) -> tuple[list[Room], int]:
    query = db.query(Room).filter(Room.service_id == service_id)
    if filters:
        query, _ = apply_filters(query, Room, filters)
    total = query.count()
    items = query.offset((page - 1) * per_page).limit(per_page).all()
    return items, total


def create(db: Session, data: RoomCreate) -> Room:
    from app.domains.room_schedule import repository as schedule_repository  # noqa: F401

    room = Room(**data.model_dump())
    db.add(room)
    db.commit()
    db.refresh(room)
    schedule_repository.create_schedule_for_room(db, room.id)
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
