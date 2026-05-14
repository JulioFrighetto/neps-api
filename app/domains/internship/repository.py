from sqlalchemy.orm import Session

from app.domains.internship.model import Internship, InternshipDocument, InternshipRecord
from app.domains.internship.schemas import (
    InternshipCreate,
    InternshipDocumentCreate,
    InternshipRecordCreate,
    InternshipRecordUpdate,
    InternshipUpdate,
)


# ── Internship ────────────────────────────────────────────────────────────────

def get_all(db: Session, skip: int = 0, limit: int = 100) -> list[Internship]:
    return db.query(Internship).offset(skip).limit(limit).all()


def get_by_id(db: Session, internship_id: int) -> Internship | None:
    return db.query(Internship).filter(Internship.id == internship_id).first()


def get_by_student(db: Session, student_id: int) -> list[Internship]:
    return db.query(Internship).filter(Internship.student_id == student_id).all()


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


# ── InternshipRecord ──────────────────────────────────────────────────────────

def get_records_by_internship(db: Session, internship_id: int) -> list[InternshipRecord]:
    return (
        db.query(InternshipRecord)
        .filter(InternshipRecord.internship_id == internship_id)
        .all()
    )


def get_records_by_student(db: Session, student_id: int) -> list[InternshipRecord]:
    return (
        db.query(InternshipRecord)
        .filter(InternshipRecord.student_id == student_id)
        .all()
    )


def get_record_by_id(db: Session, record_id: int) -> InternshipRecord | None:
    return db.query(InternshipRecord).filter(InternshipRecord.id == record_id).first()


def create_record(db: Session, data: InternshipRecordCreate) -> InternshipRecord:
    record = InternshipRecord(**data.model_dump())
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def update_record(
    db: Session, record_id: int, data: InternshipRecordUpdate
) -> InternshipRecord | None:
    record = get_record_by_id(db, record_id)
    if not record:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(record, field, value)
    db.commit()
    db.refresh(record)
    return record


# ── InternshipDocument ────────────────────────────────────────────────────────

def get_documents_by_internship(db: Session, internship_id: int) -> list[InternshipDocument]:
    return (
        db.query(InternshipDocument)
        .filter(InternshipDocument.internship_id == internship_id)
        .all()
    )


def create_document(db: Session, data: InternshipDocumentCreate) -> InternshipDocument:
    doc = InternshipDocument(**data.model_dump())
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc


def delete_document(db: Session, document_id: int) -> bool:
    doc = db.query(InternshipDocument).filter(InternshipDocument.id == document_id).first()
    if not doc:
        return False
    db.delete(doc)
    db.commit()
    return True
