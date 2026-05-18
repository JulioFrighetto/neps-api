from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.schemas import Page
from app.domains.internship_field import repository
from app.domains.internship_field.schemas import (
    InternshipFieldCreate,
    InternshipFieldResponse,
    InternshipFieldUpdate,
)

router = APIRouter(tags=["Internship Field"])


@router.get("/internship-field", response_model=Page[InternshipFieldResponse])
def list_internship_field(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if current_user.role == "admin":
        items, total = repository.get_all(db, skip=skip, limit=limit)
    elif current_user.role == "internship_field" and current_user.internship_field_id is not None:
        field = repository.get_by_id(db, current_user.internship_field_id)
        items = [field] if field else []
        total = 1 if field else 0
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado")
    return Page(items=items, total=total, skip=skip, limit=limit, has_next=skip + limit < total)


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
