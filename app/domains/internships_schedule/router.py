import math

from fastapi import APIRouter, Body, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.schemas import Page, PaginationInfo
from app.domains.internships_room.repository import get_by_id as get_internships_room_by_id
from app.domains.internships_schedule import repository
from app.domains.internships_schedule.schemas import (
    InternshipsScheduleCreate,
    InternshipsScheduleResponse,
    InternshipsScheduleUpdate,
)
from app.domains.student.repository import get_by_id as get_student_by_id

router = APIRouter(prefix="/internship-schedules", tags=["Internships Schedules"])


class InternshipsScheduleGetRequest(BaseModel):
    internships_schedule_id: int


class InternshipsSchedulesByRoomRequest(BaseModel):
    internships_room_id: int


class InternshipsSchedulesByRoomDayRequest(BaseModel):
    internships_room_id: int
    week_day: str


class InternshipsScheduleUpdateRequest(InternshipsScheduleUpdate):
    internships_schedule_id: int


@router.get("/", response_model=Page[InternshipsScheduleResponse])
def list_internships_schedules(
    page: int = Body(1, ge=1),
    per_page: int = Body(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if current_user.role == "admin":
        items, total = repository.get_all(db, page=page, per_page=per_page)
    elif current_user.role == "internships" and current_user.internships_id is not None:
        items, total = repository.get_by_internships(db, current_user.internships_id, page=page, per_page=per_page)
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


@router.post("/detail", response_model=InternshipsScheduleResponse)
def get_internships_schedule(data: InternshipsScheduleGetRequest, db: Session = Depends(get_db)):
    schedule = repository.get_by_id(db, data.internships_schedule_id)
    if not schedule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agenda não encontrada")
    return schedule


@router.post("/by-room", response_model=list[InternshipsScheduleResponse])
def list_internships_schedules_by_room(data: InternshipsSchedulesByRoomRequest, db: Session = Depends(get_db)):
    # First, check if it's a InternshipsRoom ID
    internships_schedules = repository.get_by_room(db, data.internships_room_id)
    if internships_schedules:
        return internships_schedules
    
    # If not found, check if it's a Room ID
    from app.domains.room_schedule import repository as room_schedule_repository
    room_schedules = room_schedule_repository.get_by_room(db, data.internships_room_id)
    if room_schedules:
        # Map RoomSchedule to InternshipsScheduleResponse format
        # Convert day and shift from lowercase to uppercase
        day_map = {"seg": "SEG", "ter": "TER", "qua": "QUA", "qui": "QUI", "sex": "SEX", "sab": "SAB", "dom": "DOM"}
        shift_map = {"manhã": "MAN", "tarde": "TRD", "noite": "VSP"}
        
        from app.domains.internships_schedule.schemas import InternshipsScheduleResponse
        result = []
        for rs in room_schedules:
            result.append(
                InternshipsScheduleResponse(
                    id=rs.id,
                    internships_room_id=rs.room_id,
                    week_day=day_map.get(rs.week_day, rs.week_day),
                    shift=shift_map.get(rs.shift, rs.shift),
                    is_active=rs.is_active,
                    created_at=rs.created_at,
                    updated_at=rs.updated_at,
                )
            )
        return result
    
    return []


@router.post("/by-room/by-day", response_model=list[InternshipsScheduleResponse])
def list_internships_schedules_by_room_and_day(
    data: InternshipsSchedulesByRoomDayRequest, db: Session = Depends(get_db)
):
    return repository.get_by_room_and_day(db, data.internships_room_id, data.week_day)


@router.post("/", response_model=InternshipsScheduleResponse, status_code=status.HTTP_201_CREATED)
def create_internships_schedule(data: InternshipsScheduleCreate, db: Session = Depends(get_db)):
    internships_room = get_internships_room_by_id(db, data.internships_room_id)
    if not internships_room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sala não encontrada")
    if data.student_id is not None:
        student = get_student_by_id(db, data.student_id)
        if not student:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Aluno não encontrado")
    if repository.get_by_slot(db, data.internships_room_id, data.week_day, data.shift):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Já existe agenda para esta sala, dia e turno",
        )
    return repository.create(db, data)


@router.patch("/", response_model=InternshipsScheduleResponse)
def update_internships_schedule(
    data: InternshipsScheduleUpdateRequest, db: Session = Depends(get_db)
):
    schedule = repository.get_by_id(db, data.internships_schedule_id)
    if not schedule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agenda não encontrada")

    update_payload = data.model_dump(exclude_unset=True)
    new_week_day = update_payload.get("week_day", schedule.week_day)
    new_shift = update_payload.get("shift", schedule.shift)
    new_student_id = update_payload.get("student_id", schedule.student_id)

    if "student_id" in update_payload and new_student_id is not None:
        student = get_student_by_id(db, new_student_id)
        if not student:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Aluno não encontrado")

    conflict = repository.get_by_slot(db, schedule.internships_room_id, new_week_day, new_shift)
    if conflict and conflict.id != schedule.id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Já existe agenda para esta sala, dia e turno",
        )

    updated = repository.update(db, data.internships_schedule_id, data)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agenda não encontrada")
    return updated
