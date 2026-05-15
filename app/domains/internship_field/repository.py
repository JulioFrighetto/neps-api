from sqlalchemy.orm import Session

from app.domains.internship_field.model import InternshipField, Region
from app.domains.internship_field.schemas import (
    InternshipFieldCreate,
    InternshipFieldUpdate,
    RegionCreate,
    RegionUpdate,
)


# InternshipField
def get_all(db: Session, skip: int = 0, limit: int = 100) -> list[InternshipField]:
    return db.query(InternshipField).offset(skip).limit(limit).all()


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


# Region
def get_all_regions(db: Session, skip: int = 0, limit: int = 100) -> list[Region]:
    return db.query(Region).offset(skip).limit(limit).all()


def get_region_by_id(db: Session, region_id: int) -> Region | None:
    return db.query(Region).filter(Region.id == region_id).first()


def create_region(db: Session, data: RegionCreate) -> Region:
    region = Region(**data.model_dump())
    db.add(region)
    db.commit()
    db.refresh(region)
    return region


def update_region(db: Session, region_id: int, data: RegionUpdate) -> Region | None:
    region = get_region_by_id(db, region_id)
    if not region:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(region, field, value)
    db.commit()
    db.refresh(region)
    return region


def delete_region(db: Session, region_id: int) -> bool:
    region = get_region_by_id(db, region_id)
    if not region:
        return False
    db.delete(region)
    db.commit()
    return True
