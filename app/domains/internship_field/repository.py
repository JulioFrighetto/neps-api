from sqlalchemy.orm import Session

from app.domains.internship_field.model import InternshipField
from app.domains.internship_field.schemas import (
    InternshipFieldCreate,
    InternshipFieldUpdate,
)


def get_all(db: Session, skip: int = 0, limit: int = 100) -> tuple[list[InternshipField], int]:
    query = db.query(InternshipField)
    total = query.count()
    items = query.offset(skip).limit(limit).all()
    return items, total


def get_by_id(db: Session, internship_field_id: int) -> InternshipField | None:
    return db.query(InternshipField).filter(InternshipField.id == internship_field_id).first()


def create(db: Session, data: InternshipFieldCreate) -> InternshipField:
    internship_field = InternshipField(**data.model_dump())
    db.add(internship_field)
    db.commit()
    db.refresh(internship_field)
    return internship_field


def update(db: Session, internship_field_id: int, data: InternshipFieldUpdate) -> InternshipField | None:
    internship_field = get_by_id(db, internship_field_id)
    if not internship_field:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(internship_field, field, value)
    db.commit()
    db.refresh(internship_field)
    return internship_field


def delete(db: Session, internship_field_id: int) -> bool:
    internship_field = get_by_id(db, internship_field_id)
    if not internship_field:
        return False
    db.delete(internship_field)
    db.commit()
    return True
