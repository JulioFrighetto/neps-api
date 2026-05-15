from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.domains.internship_field import repository
from app.domains.internship_field.schemas import (
    InternshipFieldCreate,
    InternshipFieldResponse,
    InternshipFieldUpdate,
)

router = APIRouter(tags=["Internship Field"])


@router.get("/internship-field", response_model=list[InternshipFieldResponse])
def list_internship_field(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return repository.get_all(db, skip=skip, limit=limit)


@router.get("/internship-field/{internship_field_id}", response_model=InternshipFieldResponse)
def get_internship_field(internship_field_id: int, db: Session = Depends(get_db)):
    hc = repository.get_by_id(db, internship_field_id)
    if not hc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="UBS não encontrada")
    return hc


@router.post("/internship-field", response_model=InternshipFieldResponse, status_code=status.HTTP_201_CREATED)
def create_internship_field(data: InternshipFieldCreate, db: Session = Depends(get_db)):
    return repository.create(db, data)


@router.patch("/internship-field/{internship_field_id}", response_model=InternshipFieldResponse)
def update_internship_field(
    internship_field_id: int, data: InternshipFieldUpdate, db: Session = Depends(get_db)
):
    hc = repository.update(db, internship_field_id, data)
    if not hc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="UBS não encontrada")
    return hc


@router.delete("/internship-field/{internship_field_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_internship_field(internship_field_id: int, db: Session = Depends(get_db)):
    deleted = repository.delete(db, internship_field_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="UBS não encontrada")
