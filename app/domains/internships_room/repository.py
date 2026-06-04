from sqlalchemy.orm import Session

from app.domains.internships_room.model import InternshipsRoom
from app.domains.internships_room.schemas import InternshipsRoomCreate, InternshipsRoomUpdate


def get_all(db: Session, page: int = 1, per_page: int = 10) -> tuple[list[InternshipsRoom], int]:
    query = db.query(InternshipsRoom)
    total = query.count()
    items = query.offset((page - 1) * per_page).limit(per_page).all()
    return items, total


def get_by_id(db: Session, internships_room_id: int) -> InternshipsRoom | None:
    return db.query(InternshipsRoom).filter(InternshipsRoom.id == internships_room_id).first()


def get_by_internships(db: Session, internships_id: int, page: int = 1, per_page: int = 10) -> tuple[list[InternshipsRoom], int]:
    query = db.query(InternshipsRoom).filter(InternshipsRoom.internships_id == internships_id)
    total = query.count()
    items = query.offset((page - 1) * per_page).limit(per_page).all()
    return items, total


def create(db: Session, data: InternshipsRoomCreate) -> InternshipsRoom:
    internships_room = InternshipsRoom(**data.model_dump())
    db.add(internships_room)
    db.commit()
    db.refresh(internships_room)
    return internships_room


def update(db: Session, internships_room_id: int, data: InternshipsRoomUpdate) -> InternshipsRoom | None:
    internships_room = get_by_id(db, internships_room_id)
    if not internships_room:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(internships_room, field, value)
    db.commit()
    db.refresh(internships_room)
    return internships_room


def delete(db: Session, internships_room_id: int) -> bool:
    internships_room = get_by_id(db, internships_room_id)
    if not internships_room:
        return False
    db.delete(internships_room)
    db.commit()
    return True
