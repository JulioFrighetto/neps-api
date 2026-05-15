from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.domains.region import repository
from app.domains.region.schemas import (
    RegionCreate,
    RegionResponse,
    RegionUpdate,
)

router = APIRouter(tags=["Region"])


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
