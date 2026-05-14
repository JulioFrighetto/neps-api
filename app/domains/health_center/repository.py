from sqlalchemy.orm import Session

from app.domains.health_center.model import HealthCenter, Region
from app.domains.health_center.schemas import (
    HealthCenterCreate,
    HealthCenterUpdate,
    RegionCreate,
    RegionUpdate,
)


# HealthCenter
def get_all(db: Session, skip: int = 0, limit: int = 100) -> list[HealthCenter]:
    return db.query(HealthCenter).offset(skip).limit(limit).all()


def get_by_id(db: Session, health_center_id: int) -> HealthCenter | None:
    return db.query(HealthCenter).filter(HealthCenter.id == health_center_id).first()


def create(db: Session, data: HealthCenterCreate) -> HealthCenter:
    health_center = HealthCenter(**data.model_dump())
    db.add(health_center)
    db.commit()
    db.refresh(health_center)
    return health_center


def update(db: Session, health_center_id: int, data: HealthCenterUpdate) -> HealthCenter | None:
    health_center = get_by_id(db, health_center_id)
    if not health_center:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(health_center, field, value)
    db.commit()
    db.refresh(health_center)
    return health_center


def delete(db: Session, health_center_id: int) -> bool:
    health_center = get_by_id(db, health_center_id)
    if not health_center:
        return False
    db.delete(health_center)
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
