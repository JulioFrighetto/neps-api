import math

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.schemas import Page, PaginationInfo
from app.domains.service.repository import get_by_id as get_service_by_id
from app.domains.service_room import repository
from app.domains.service_room.schemas import (
    ServiceRoomCreate,
    ServiceRoomResponse,
    ServiceRoomUpdate,
)

router = APIRouter(prefix="/service-rooms", tags=["Service Rooms"])


@router.get("/", response_model=Page[ServiceRoomResponse])
def list_service_rooms(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if current_user.role == "admin":
        items, total = repository.get_all(db, page=page, per_page=per_page)
    elif current_user.role == "service" and current_user.service_id is not None:
        items, total = repository.get_by_service(db, current_user.service_id, page=page, per_page=per_page)
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


@router.get("/{service_room_id}", response_model=ServiceRoomResponse)
def get_service_room(service_room_id: int, db: Session = Depends(get_db)):
    service_room = repository.get_by_id(db, service_room_id)
    if not service_room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sala não encontrada")
    return service_room


@router.get("/by-service/{service_id}", response_model=Page[ServiceRoomResponse])
def list_service_rooms_by_service(service_id: int, page: int = Query(1, ge=1), per_page: int = Query(10, ge=1, le=100), db: Session = Depends(get_db)):
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


@router.post("/", response_model=ServiceRoomResponse, status_code=status.HTTP_201_CREATED)
def create_service_room(data: ServiceRoomCreate, db: Session = Depends(get_db)):
    service = get_service_by_id(db, data.service_id)
    if not service:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Serviço não encontrado")
    return repository.create(db, data)


@router.patch("/{service_room_id}", response_model=ServiceRoomResponse)
def update_service_room(service_room_id: int, data: ServiceRoomUpdate, db: Session = Depends(get_db)):
    service_room = repository.update(db, service_room_id, data)
    if not service_room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sala não encontrada")
    return service_room
