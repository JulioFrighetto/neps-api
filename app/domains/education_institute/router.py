from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.domains.education_institute import repository
from app.domains.education_institute.schemas import (
    EducationInstituteCreate,
    EducationInstituteResponse,
    EducationInstituteUpdate,
)

router = APIRouter(prefix="/education-institutes", tags=["Education Institutes"])


@router.get("/", response_model=list[EducationInstituteResponse])
def list_institutes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return repository.get_all(db, skip=skip, limit=limit)


@router.get("/{institute_id}", response_model=EducationInstituteResponse)
def get_institute(institute_id: int, db: Session = Depends(get_db)):
    institute = repository.get_by_id(db, institute_id)
    if not institute:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Instituição não encontrada")
    return institute


@router.post("/", response_model=EducationInstituteResponse, status_code=status.HTTP_201_CREATED)
def create_institute(data: EducationInstituteCreate, db: Session = Depends(get_db)):
    return repository.create(db, data)


@router.patch("/{institute_id}", response_model=EducationInstituteResponse)
def update_institute(
    institute_id: int, data: EducationInstituteUpdate, db: Session = Depends(get_db)
):
    institute = repository.update(db, institute_id, data)
    if not institute:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Instituição não encontrada")
    return institute


@router.delete("/{institute_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_institute(institute_id: int, db: Session = Depends(get_db)):
    deleted = repository.delete(db, institute_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Instituição não encontrada")
