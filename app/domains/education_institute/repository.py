from sqlalchemy.orm import Session

from app.domains.education_institute.model import EducationInstitute
from app.domains.education_institute.schemas import (
    EducationInstituteCreate,
    EducationInstituteUpdate,
)


def get_all(db: Session, skip: int = 0, limit: int = 100) -> list[EducationInstitute]:
    return db.query(EducationInstitute).offset(skip).limit(limit).all()


def get_by_id(db: Session, institute_id: int) -> EducationInstitute | None:
    return db.query(EducationInstitute).filter(EducationInstitute.id == institute_id).first()


def create(db: Session, data: EducationInstituteCreate) -> EducationInstitute:
    institute = EducationInstitute(**data.model_dump())
    db.add(institute)
    db.commit()
    db.refresh(institute)
    return institute


def update(
    db: Session, institute_id: int, data: EducationInstituteUpdate
) -> EducationInstitute | None:
    institute = get_by_id(db, institute_id)
    if not institute:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(institute, field, value)
    db.commit()
    db.refresh(institute)
    return institute


def delete(db: Session, institute_id: int) -> bool:
    institute = get_by_id(db, institute_id)
    if not institute:
        return False
    db.delete(institute)
    db.commit()
    return True
