from sqlalchemy.orm import Session

from app.core.filters import apply_filters
from app.domains.region.model import Region
from app.domains.region.schemas import (
    RegionCreate,
    RegionUpdate,
)


# Region
def get_all_regions(db: Session, page: int = 1, per_page: int = 10, filters: dict | None = None) -> tuple[list[Region], int]:
    query = db.query(Region)
    if filters:
        query, _ = apply_filters(query, Region, filters)
    total = query.count()
    items = query.offset((page - 1) * per_page).limit(per_page).all()
    return items, total


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
