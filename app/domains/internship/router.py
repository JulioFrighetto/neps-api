from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.schemas import Page
from app.domains.internship import repository
from app.domains.internship.schemas import (
    InternshipCreate,
    InternshipResponse,
    InternshipUpdate,
)

router = APIRouter(tags=["Internships"])


@router.get("/internships", response_model=Page[InternshipResponse])
def list_internships(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if current_user.role == "admin":
        items, total = repository.get_all(db, skip=skip, limit=limit)
    elif current_user.role == "education_institute" and current_user.education_institute_id is not None:
        items, total = repository.get_by_edu_institute(
            db, current_user.education_institute_id, skip=skip, limit=limit
        )
    elif current_user.role == "internship_field" and current_user.internship_field_id is not None:
        items, total = repository.get_by_field(db, current_user.internship_field_id, skip=skip, limit=limit)
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado")
    return Page(items=items, total=total, skip=skip, limit=limit, has_next=skip + limit < total)


@router.get("/internships/{internship_id}", response_model=InternshipResponse)
def get_internship(internship_id: int, db: Session = Depends(get_db)):
    internship = repository.get_by_id(db, internship_id)
    if not internship:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Estágio não encontrado")
    return internship

@router.get("/internships/by-field/{field_id}", response_model=Page[InternshipResponse])
def list_internships_by_field(field_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items, total = repository.get_by_field(db, field_id, skip=skip, limit=limit)
    return Page(items=items, total=total, skip=skip, limit=limit, has_next=skip + limit < total)

@router.get("/internships/by-education-institute/{edu_institute_id}", response_model=Page[InternshipResponse])
def list_internships_by_edu_institute(edu_institute_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items, total = repository.get_by_edu_institute(db, edu_institute_id, skip=skip, limit=limit)
    return Page(items=items, total=total, skip=skip, limit=limit, has_next=skip + limit < total)

@router.get("/internships/by-room/{room_id}", response_model=Page[InternshipResponse])
def list_internships_by_room(room_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items, total = repository.get_by_room(db, room_id, skip=skip, limit=limit)
    return Page(items=items, total=total, skip=skip, limit=limit, has_next=skip + limit < total)


@router.post("/internships", response_model=InternshipResponse, status_code=status.HTTP_201_CREATED)
def create_internship(data: InternshipCreate, db: Session = Depends(get_db)):
    return repository.create(db, data)


@router.patch("/internships/{internship_id}", response_model=InternshipResponse)
def update_internship(internship_id: int, data: InternshipUpdate, db: Session = Depends(get_db)):
    internship = repository.update(db, internship_id, data)
    if not internship:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Estágio não encontrado")
    return internship
