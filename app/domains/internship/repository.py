from sqlalchemy.orm import Session

from app.domains.room.model import Room
from app.domains.student.model import Student
from app.domains.internship.model import Internship
from app.domains.internship.schemas import (
    InternshipCreate,
    InternshipUpdate,
)


def get_all(db: Session, skip: int = 0, limit: int = 100) -> list[Internship]:
    return db.query(Internship).offset(skip).limit(limit).all()


def get_by_id(db: Session, internship_id: int) -> Internship | None:
    return db.query(Internship).filter(Internship.id == internship_id).first()

def get_by_edu_institute(db: Session, edu_institute: int) -> list[Internship]:
    return db.query(Internship)\
        .join(Student, Internship.student_id == Student.id)\
        .filter(Student.edu_institute_id == edu_institute)\
        .all()

def get_by_field(db: Session, field_id: int) -> list[Internship]:
    return db.query(Internship)\
        .join(Room, Internship.room_id == Room.id)\
        .filter(Room.field_id == field_id)\
        .all()

def get_by_room(db: Session, room_id: int) -> list[Internship]:
    return db.query(Internship).filter(Internship.room_id == room_id).all()


def create(db: Session, data: InternshipCreate) -> Internship:
    internship = Internship(**data.model_dump())
    db.add(internship)
    db.commit()
    db.refresh(internship)
    return internship


def update(db: Session, internship_id: int, data: InternshipUpdate) -> Internship | None:
    internship = get_by_id(db, internship_id)
    if not internship:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(internship, field, value)
    db.commit()
    db.refresh(internship)
    return internship


def delete(db: Session, internship_id: int) -> bool:
    internship = get_by_id(db, internship_id)
    if not internship:
        return False
    db.delete(internship)
    db.commit()
    return True
