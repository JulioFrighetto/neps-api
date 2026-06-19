import math

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.schemas import FilterInfo, Page, PaginationInfo
from app.domains.region import repository
from app.domains.region.schemas import (RegionCreate, RegionResponse,
                                        RegionUpdate)

router = APIRouter(tags=["Region"])

AVAILABLE_FILTERS = ["name_like", "is_active"]


class RegionGetRequest(BaseModel):
    region_id: int


class RegionUpdateRequest(RegionUpdate):
    region_id: int


@router.get("/regions", response_model=Page[RegionResponse])
def list_regions(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=500),
    name_like: str | None = Query(None),
    is_active: bool | None = Query(None),
    db: Session = Depends(get_db),
):
    filters = {k: v for k, v in {"name_like": name_like, "is_active": is_active}.items() if v is not None}
    items, total = repository.get_all_regions(db, page=page, per_page=per_page, filters=filters)
    return Page(
        items=items,
        pagination=PaginationInfo(
            page=page,
            per_page=per_page,
            total=total,
            total_pages=max(1, math.ceil(total / per_page)) if total > 0 else 0,
        ),
        filters=FilterInfo(applied=list(filters.keys()), available=AVAILABLE_FILTERS),
    )


@router.post("/regions/detail", response_model=RegionResponse)
def get_region(data: RegionGetRequest, db: Session = Depends(get_db)):
    region = repository.get_region_by_id(db, data.region_id)
    if not region:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Território não encontrado")
    return region


@router.post("/regions", response_model=RegionResponse, status_code=status.HTTP_201_CREATED)
def create_region(data: RegionCreate, db: Session = Depends(get_db)):
    return repository.create_region(db, data)


@router.patch("/regions", response_model=RegionResponse)
def update_region(data: RegionUpdateRequest, db: Session = Depends(get_db)):
    region = repository.update_region(db, data.region_id, data)
    if not region:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Território não encontrado")
    return region
