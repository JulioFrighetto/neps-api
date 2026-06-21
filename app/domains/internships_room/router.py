import math

from fastapi import APIRouter, Body, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.schemas import Page, PaginationInfo
from app.domains.internships.repository import get_by_id as get_internships_by_id
from app.domains.internships_room import repository
from app.domains.internships_room.schemas import (
    InternshipsRoomCreate,
    InternshipsRoomResponse,
    InternshipsRoomUpdate,
)

router = APIRouter(prefix="/internships-rooms", tags=["Internships Rooms"])


class InternshipsRoomGetRequest(BaseModel):
    internships_room_id: int


class InternshipsRoomsByInternshipsRequest(BaseModel):
    internship_id: int
    page: int = 1
    per_page: int = 10


class InternshipsRoomUpdateRequest(InternshipsRoomUpdate):
    internships_room_id: int


@router.get("/", response_model=Page[InternshipsRoomResponse])
def list_internships_rooms(
    page: int = Body(1, ge=1),
    per_page: int = Body(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if current_user.role == "admin":
        items, total = repository.get_all(db, page=page, per_page=per_page)
    elif current_user.role == "internships" and current_user.internship_id is not None:
        items, total = repository.get_by_internships(db, current_user.internship_id, page=page, per_page=per_page)
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado")
    return Page(
        items=items,
        pagination=PaginationInfo(
            page=page,
            per_page=per_page,
            total=total,
            total_pages=max(1, math.ceil(total / per_page)) if total > 0 else 0,
        ),
    )


@router.post("/detail", response_model=InternshipsRoomResponse)
def get_internships_room(data: InternshipsRoomGetRequest, db: Session = Depends(get_db)):
    internships_room = repository.get_by_id(db, data.internships_room_id)
    if not internships_room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sala não encontrada")
    return internships_room




@router.post("/by-internships", response_model=Page[InternshipsRoomResponse])
def list_internships_rooms_by_internship(data: InternshipsRoomsByInternshipsRequest, db: Session = Depends(get_db)):
    items, total = repository.get_by_internships(db, data.internship_id, page=data.page, per_page=data.per_page)
    return Page(
        items=items,
        pagination=PaginationInfo(
            page=data.page,
            per_page=data.per_page,
            total=total,
            total_pages=max(1, math.ceil(total / data.per_page)) if total > 0 else 0,
        ),
    )


@router.post("/", response_model=InternshipsRoomResponse, status_code=status.HTTP_201_CREATED)
def create_internships_room(data: InternshipsRoomCreate, db: Session = Depends(get_db)):
    internships = get_internships_by_id(db, data.internship_id)
    if not internships:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campo de estágio não encontrado")
    return repository.create(db, data)


@router.patch("/", response_model=InternshipsRoomResponse)
def update_internships_room(data: InternshipsRoomUpdateRequest, db: Session = Depends(get_db)):
    internships_room = repository.update(db, data.internships_room_id, data)
    if not internships_room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sala não encontrada")
    return internships_room
