from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.domains.health_center import repository
from app.domains.health_center.schemas import (
    HealthCenterCreate,
    HealthCenterResponse,
    HealthCenterUpdate,
    RegionCreate,
    RegionResponse,
    RegionUpdate,
)

router = APIRouter(tags=["Health Centers"])


# ── Health Centers ────────────────────────────────────────────────────────────

@router.get("/health-centers", response_model=list[HealthCenterResponse])
def list_health_centers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return repository.get_all(db, skip=skip, limit=limit)


@router.get("/health-centers/{health_center_id}", response_model=HealthCenterResponse)
def get_health_center(health_center_id: int, db: Session = Depends(get_db)):
    hc = repository.get_by_id(db, health_center_id)
    if not hc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="UBS não encontrada")
    return hc


@router.post("/health-centers", response_model=HealthCenterResponse, status_code=status.HTTP_201_CREATED)
def create_health_center(data: HealthCenterCreate, db: Session = Depends(get_db)):
    return repository.create(db, data)


@router.patch("/health-centers/{health_center_id}", response_model=HealthCenterResponse)
def update_health_center(
    health_center_id: int, data: HealthCenterUpdate, db: Session = Depends(get_db)
):
    hc = repository.update(db, health_center_id, data)
    if not hc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="UBS não encontrada")
    return hc


@router.delete("/health-centers/{health_center_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_health_center(health_center_id: int, db: Session = Depends(get_db)):
    deleted = repository.delete(db, health_center_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="UBS não encontrada")


# ── Regions ───────────────────────────────────────────────────────────────────

@router.get("/regions", response_model=list[RegionResponse])
def list_regions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return repository.get_all_regions(db, skip=skip, limit=limit)


@router.get("/regions/{region_id}", response_model=RegionResponse)
def get_region(region_id: int, db: Session = Depends(get_db)):
    region = repository.get_region_by_id(db, region_id)
    if not region:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Região não encontrada")
    return region


@router.post("/regions", response_model=RegionResponse, status_code=status.HTTP_201_CREATED)
def create_region(data: RegionCreate, db: Session = Depends(get_db)):
    return repository.create_region(db, data)


@router.patch("/regions/{region_id}", response_model=RegionResponse)
def update_region(region_id: int, data: RegionUpdate, db: Session = Depends(get_db)):
    region = repository.update_region(db, region_id, data)
    if not region:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Região não encontrada")
    return region


@router.delete("/regions/{region_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_region(region_id: int, db: Session = Depends(get_db)):
    deleted = repository.delete_region(db, region_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Região não encontrada")
