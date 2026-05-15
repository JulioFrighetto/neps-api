from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.domains.internship import repository
from app.domains.internship.schemas import (
    InternshipCreate,
    InternshipResponse,
    InternshipUpdate,
)

router = APIRouter(tags=["Internships"])


@router.get("/internships", response_model=list[InternshipResponse])
def list_internships(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return repository.get_all(db, skip=skip, limit=limit)


@router.get("/internships/{internship_id}", response_model=InternshipResponse)
def get_internship(internship_id: int, db: Session = Depends(get_db)):
    internship = repository.get_by_id(db, internship_id)
    if not internship:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Estágio não encontrado")
    return internship

@router.get("/internships/by-field/{field_id}", response_model=list[InternshipResponse])
def list_internships_by_field(field_id: int, db: Session = Depends(get_db)):
    return repository.get_by_field(db, field_id)

@router.get("/internships/by-education-institute/{edu_institute_id}", response_model=list[InternshipResponse])
def list_internships_by_edu_institute(edu_institute_id: int, db: Session = Depends(get_db)):
    return repository.get_by_edu_institute(db, edu_institute_id)

@router.get("/internships/by-room/{room_id}", response_model=list[InternshipResponse])
def list_internships_by_room(room_id: int, db: Session = Depends(get_db)):
    return repository.get_by_room(db, room_id)


@router.post("/internships", response_model=InternshipResponse, status_code=status.HTTP_201_CREATED)
def create_internship(data: InternshipCreate, db: Session = Depends(get_db)):
    return repository.create(db, data)


@router.patch("/internships/{internship_id}", response_model=InternshipResponse)
def update_internship(internship_id: int, data: InternshipUpdate, db: Session = Depends(get_db)):
    internship = repository.update(db, internship_id, data)
    if not internship:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Estágio não encontrado")
    return internship


@router.delete("/internships/{internship_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_internship(internship_id: int, db: Session = Depends(get_db)):
    deleted = repository.delete(db, internship_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Estágio não encontrado")
