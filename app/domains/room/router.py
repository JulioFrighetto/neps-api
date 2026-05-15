from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.domains.room import repository
from app.domains.room.schemas import (
    RoomCreate,
    RoomResponse,
    RoomUpdate,
)

router = APIRouter(prefix="/rooms", tags=["Rooms"])


@router.get("/", response_model=list[RoomResponse])
def list_rooms(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return repository.get_all(db, skip=skip, limit=limit)


@router.get("/{room_id}", response_model=RoomResponse)
def get_room(room_id: int, db: Session = Depends(get_db)):
    room = repository.get_by_id(db, room_id)
    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sala não encontrada")
    return room


@router.get("/by-internship_field/{internship_field_id}", response_model=list[RoomResponse])
def list_rooms_by_internship_field(internship_field_id: int, db: Session = Depends(get_db)):
    return repository.get_by_internship_field(db, internship_field_id)


@router.post("/", response_model=RoomResponse, status_code=status.HTTP_201_CREATED)
def create_room(data: RoomCreate, db: Session = Depends(get_db)):
    return repository.create(db, data)


@router.patch("/{room_id}", response_model=RoomResponse)
def update_room(room_id: int, data: RoomUpdate, db: Session = Depends(get_db)):
    room = repository.update(db, room_id, data)
    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sala não encontrada")
    return room


@router.delete("/{room_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_room(room_id: int, db: Session = Depends(get_db)):
    deleted = repository.delete(db, room_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sala não encontrada")
