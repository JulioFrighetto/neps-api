import math

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.schemas import FilterInfo, Page, PaginationInfo
from app.domains.room import repository
from app.domains.room.schemas import (
    RoomCreate,
    RoomResponse,
    RoomUpdate,
)

router = APIRouter(prefix="/rooms", tags=["Rooms"])

AVAILABLE_FILTERS = ["name_like", "internship_id", "has_gurney", "capacity_min", "capacity_max"]


class RoomGetRequest(BaseModel):
    room_id: int


class RoomsByInternshipsRequest(BaseModel):
    internship_id: int
    page: int = 1
    per_page: int = 10


class RoomUpdateRequest(RoomUpdate):
    room_id: int


@router.get("/", response_model=Page[RoomResponse])
def list_rooms(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    name_like: str | None = Query(None),
    internship_id: int | None = Query(None),
    has_gurney: bool | None = Query(None),
    capacity_min: int | None = Query(None),
    capacity_max: int | None = Query(None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    filters = {}
    if name_like is not None:
        filters["name_like"] = name_like
    if internship_id is not None:
        filters["internship_id"] = internship_id
    if has_gurney is not None:
        filters["has_gurney"] = has_gurney
    if capacity_min is not None:
        filters["capacity_min"] = capacity_min
    if capacity_max is not None:
        filters["capacity_max"] = capacity_max

    if current_user.role == "admin":
        items, total = repository.get_all(db, page=page, per_page=per_page, filters=filters)
    elif current_user.role == "internships" and current_user.internship_id is not None:
        items, total = repository.get_by_internships(
            db, current_user.internship_id, page=page, per_page=per_page, filters=filters
        )
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
        filters=FilterInfo(applied=list(filters.keys()), available=AVAILABLE_FILTERS),
    )


@router.post("/detail", response_model=RoomResponse)
def get_room(data: RoomGetRequest, db: Session = Depends(get_db)):
    room = repository.get_by_id(db, data.room_id)
    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sala não encontrada")
    return room


@router.post("/by-internships", response_model=Page[RoomResponse])
def list_rooms_by_internships(data: RoomsByInternshipsRequest, db: Session = Depends(get_db)):
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


@router.post("/", response_model=RoomResponse, status_code=status.HTTP_201_CREATED)
def create_room(data: RoomCreate, db: Session = Depends(get_db)):
    return repository.create(db, data)


@router.patch("/", response_model=RoomResponse)
def update_room(data: RoomUpdateRequest, db: Session = Depends(get_db)):
    room = repository.update(db, data.room_id, data)
    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sala não encontrada")
    return room
