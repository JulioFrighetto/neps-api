from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.schemas import Page
from app.domains.room import repository
from app.domains.room.schemas import (
    RoomCreate,
    RoomResponse,
    RoomUpdate,
)

router = APIRouter(prefix="/rooms", tags=["Rooms"])


@router.get("/", response_model=Page[RoomResponse])
def list_rooms(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if current_user.role == "admin":
        items, total = repository.get_all(db, skip=skip, limit=limit)
    elif current_user.role == "service" and current_user.service_id is not None:
        items, total = repository.get_by_service(
            db, current_user.service_id, skip=skip, limit=limit
        )
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado")
    return Page(items=items, total=total, skip=skip, limit=limit, has_next=skip + limit < total)


@router.get("/{room_id}", response_model=RoomResponse)
def get_room(room_id: int, db: Session = Depends(get_db)):
    room = repository.get_by_id(db, room_id)
    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sala não encontrada")
    return room


@router.get("/by-service/{service_id}", response_model=Page[RoomResponse])
def list_rooms_by_service(service_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items, total = repository.get_by_service(db, service_id, skip=skip, limit=limit)
    return Page(items=items, total=total, skip=skip, limit=limit, has_next=skip + limit < total)


@router.post("/", response_model=RoomResponse, status_code=status.HTTP_201_CREATED)
def create_room(data: RoomCreate, db: Session = Depends(get_db)):
    return repository.create(db, data)


@router.patch("/{room_id}", response_model=RoomResponse)
def update_room(room_id: int, data: RoomUpdate, db: Session = Depends(get_db)):
    room = repository.update(db, room_id, data)
    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sala não encontrada")
    return room
