from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.domains.education_institution import repository
from app.domains.education_institution.schemas import (
    EducationInstitutionCreate,
    EducationInstitutionResponse,
    EducationInstitutionUpdate,
)

router = APIRouter(prefix="/education-institutions", tags=["Education Institutions"])


@router.get("/", response_model=list[EducationInstitutionResponse])
def list_institutions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return repository.get_all(db, skip=skip, limit=limit)


@router.get("/{institution_id}", response_model=EducationInstitutionResponse)
def get_institution(institution_id: int, db: Session = Depends(get_db)):
    institution = repository.get_by_id(db, institution_id)
    if not institution:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Instituição não encontrada")
    return institution


@router.post("/", response_model=EducationInstitutionResponse, status_code=status.HTTP_201_CREATED)
def create_institution(data: EducationInstitutionCreate, db: Session = Depends(get_db)):
    return repository.create(db, data)


@router.patch("/{institution_id}", response_model=EducationInstitutionResponse)
def update_institution(
    institution_id: int, data: EducationInstitutionUpdate, db: Session = Depends(get_db)
):
    institution = repository.update(db, institution_id, data)
    if not institution:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Instituição não encontrada")
    return institution


@router.delete("/{institution_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_institution(institution_id: int, db: Session = Depends(get_db)):
    deleted = repository.delete(db, institution_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Instituição não encontrada")
