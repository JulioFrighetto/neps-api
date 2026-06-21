from datetime import datetime

from sqlalchemy.orm import Query, Session, selectinload

from app.core.filters import apply_filters
from app.domains.room.model import Room
from app.domains.room.schemas import (
    RoomCreate,
    RoomUpdate,
)


def _base_query(db: Session) -> Query:
    return db.query(Room).options(selectinload(Room.internships))


def get_all(db: Session, page: int = 1, per_page: int = 10, filters: dict | None = None) -> tuple[list[Room], int]:
    query = _base_query(db)
    if filters:
        query, _ = apply_filters(query, Room, filters)
    total = query.count()
    items = query.offset((page - 1) * per_page).limit(per_page).all()
    return items, total


def get_by_id(db: Session, room_id: int) -> Room | None:
    return _base_query(db).filter(Room.id == room_id).first()


def get_by_internships(db: Session, internship_id: int, page: int = 1, per_page: int = 10, filters: dict | None = None) -> tuple[list[Room], int]:
    query = _base_query(db).filter(Room.internship_id == internship_id)
    if filters:
        query, _ = apply_filters(query, Room, filters)
    total = query.count()
    items = query.offset((page - 1) * per_page).limit(per_page).all()
    return items, total


def create(db: Session, data: RoomCreate) -> Room:
    from app.domains.room_schedule import repository_nested as schedule_repository

    room = Room(**data.model_dump())
    now = datetime.now()
    room.created_at = now
    room.updated_at = now
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
