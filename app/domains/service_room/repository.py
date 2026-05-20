from sqlalchemy.orm import Session

from app.domains.service_room.model import ServiceRoom
from app.domains.service_room.schemas import ServiceRoomCreate, ServiceRoomUpdate


def get_all(db: Session, skip: int = 0, limit: int = 100) -> tuple[list[ServiceRoom], int]:
    query = db.query(ServiceRoom)
    total = query.count()
    items = query.offset(skip).limit(limit).all()
    return items, total


def get_by_id(db: Session, service_room_id: int) -> ServiceRoom | None:
    return db.query(ServiceRoom).filter(ServiceRoom.id == service_room_id).first()


def get_by_service(db: Session, service_id: int, skip: int = 0, limit: int = 100) -> tuple[list[ServiceRoom], int]:
    query = db.query(ServiceRoom).filter(ServiceRoom.service_id == service_id)
    total = query.count()
    items = query.offset(skip).limit(limit).all()
    return items, total


def create(db: Session, data: ServiceRoomCreate) -> ServiceRoom:
    service_room = ServiceRoom(**data.model_dump())
    db.add(service_room)
    db.commit()
    db.refresh(service_room)
    return service_room


def update(db: Session, service_room_id: int, data: ServiceRoomUpdate) -> ServiceRoom | None:
    service_room = get_by_id(db, service_room_id)
    if not service_room:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(service_room, field, value)
    db.commit()
    db.refresh(service_room)
    return service_room


def delete(db: Session, service_room_id: int) -> bool:
    service_room = get_by_id(db, service_room_id)
    if not service_room:
        return False
    db.delete(service_room)
    db.commit()
    return True
