import math

from fastapi import APIRouter, Depends, HTTPException, Query, status
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

AVAILABLE_FILTERS = ["name_like", "service_id", "has_gurney", "capacity_min", "capacity_max"]


@router.get("/", response_model=Page[RoomResponse])
def list_rooms(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    name_like: str | None = Query(None),
    service_id: int | None = Query(None),
    has_gurney: bool | None = Query(None),
    capacity_min: int | None = Query(None),
    capacity_max: int | None = Query(None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    filters = {k: v for k, v in {"name_like": name_like, "service_id": service_id, "has_gurney": has_gurney, "capacity_min": capacity_min, "capacity_max": capacity_max}.items() if v is not None}

    if current_user.role == "admin":
        items, total = repository.get_all(db, page=page, per_page=per_page, filters=filters)
    elif current_user.role == "service" and current_user.service_id is not None:
        items, total = repository.get_by_service(
            db, current_user.service_id, page=page, per_page=per_page, filters=filters
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


@router.get("/{room_id}", response_model=RoomResponse)
def get_room(room_id: int, db: Session = Depends(get_db)):
    room = repository.get_by_id(db, room_id)
    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sala não encontrada")
    return room


@router.get("/by-service/{service_id}", response_model=Page[RoomResponse])
def list_rooms_by_service(service_id: int, page: int = Query(1, ge=1), per_page: int = Query(10, ge=1, le=100), db: Session = Depends(get_db)):
    items, total = repository.get_by_service(db, service_id, page=page, per_page=per_page)
    return Page(
        items=items,
        pagination=PaginationInfo(
            page=page,
            per_page=per_page,
            total=total,
            total_pages=max(1, math.ceil(total / per_page)) if total > 0 else 0,
        ),
    )


@router.post("/", response_model=RoomResponse, status_code=status.HTTP_201_CREATED)
def create_room(data: RoomCreate, db: Session = Depends(get_db)):
    return repository.create(db, data)


@router.patch("/{room_id}", response_model=RoomResponse)
def update_room(room_id: int, data: RoomUpdate, db: Session = Depends(get_db)):
    room = repository.update(db, room_id, data)
    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sala não encontrada")
    return room
