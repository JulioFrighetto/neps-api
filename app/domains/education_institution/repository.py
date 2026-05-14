from sqlalchemy.orm import Session

from app.domains.education_institution.model import EducationInstitution
from app.domains.education_institution.schemas import (
    EducationInstitutionCreate,
    EducationInstitutionUpdate,
)


def get_all(db: Session, skip: int = 0, limit: int = 100) -> list[EducationInstitution]:
    return db.query(EducationInstitution).offset(skip).limit(limit).all()


def get_by_id(db: Session, institution_id: int) -> EducationInstitution | None:
    return db.query(EducationInstitution).filter(EducationInstitution.id == institution_id).first()


def create(db: Session, data: EducationInstitutionCreate) -> EducationInstitution:
    institution = EducationInstitution(**data.model_dump())
    db.add(institution)
    db.commit()
    db.refresh(institution)
    return institution


def update(
    db: Session, institution_id: int, data: EducationInstitutionUpdate
) -> EducationInstitution | None:
    institution = get_by_id(db, institution_id)
    if not institution:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(institution, field, value)
    db.commit()
    db.refresh(institution)
    return institution


def delete(db: Session, institution_id: int) -> bool:
    institution = get_by_id(db, institution_id)
    if not institution:
        return False
    db.delete(institution)
    db.commit()
    return True
