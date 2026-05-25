import math

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.schemas import Page, PaginationInfo
from app.domains.service_room.repository import get_by_id as get_service_room_by_id
from app.domains.service_schedule import repository
from app.domains.service_schedule.schemas import (
    ServiceScheduleCreate,
    ServiceScheduleResponse,
    ServiceScheduleUpdate,
)
from app.domains.student.repository import get_by_id as get_student_by_id

router = APIRouter(prefix="/service-schedules", tags=["Service Schedules"])


@router.get("/", response_model=Page[ServiceScheduleResponse])
def list_service_schedules(
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


@router.get("/{service_schedule_id}", response_model=ServiceScheduleResponse)
def get_service_schedule(service_schedule_id: int, db: Session = Depends(get_db)):
    schedule = repository.get_by_id(db, service_schedule_id)
    if not schedule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agenda não encontrada")
    return schedule


@router.get("/by-room/{service_room_id}", response_model=list[ServiceScheduleResponse])
def list_service_schedules_by_room(service_room_id: int, db: Session = Depends(get_db)):
    # First, check if it's a ServiceRoom ID
    service_schedules = repository.get_by_room(db, service_room_id)
    if service_schedules:
        return service_schedules
    
    # If not found, check if it's a Room ID
    from app.domains.room_schedule import repository as room_schedule_repository
    room_schedules = room_schedule_repository.get_by_room(db, service_room_id)
    if room_schedules:
        # Map RoomSchedule to ServiceScheduleResponse format
        # Convert day and shift from lowercase to uppercase
        day_map = {"seg": "SEG", "ter": "TER", "qua": "QUA", "qui": "QUI", "sex": "SEX", "sab": "SAB", "dom": "DOM"}
        shift_map = {"manhã": "MAN", "tarde": "TRD", "noite": "VSP"}
        
        from app.domains.service_schedule.schemas import ServiceScheduleResponse
        result = []
        for rs in room_schedules:
            result.append(
                ServiceScheduleResponse(
                    id=rs.id,
                    service_room_id=rs.room_id,
                    week_day=day_map.get(rs.week_day, rs.week_day),
                    shift=shift_map.get(rs.shift, rs.shift),
                    is_active=rs.is_active,
                    created_at=rs.created_at,
                    updated_at=rs.updated_at,
                )
            )
        return result
    
    return []


@router.get("/by-room/{service_room_id}/by-day/{week_day}", response_model=list[ServiceScheduleResponse])
def list_service_schedules_by_room_and_day(
    service_room_id: int, week_day: str, db: Session = Depends(get_db)
):
    return repository.get_by_room_and_day(db, service_room_id, week_day)


@router.post("/", response_model=ServiceScheduleResponse, status_code=status.HTTP_201_CREATED)
def create_service_schedule(data: ServiceScheduleCreate, db: Session = Depends(get_db)):
    service_room = get_service_room_by_id(db, data.service_room_id)
    if not service_room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sala não encontrada")
    if data.student_id is not None:
        student = get_student_by_id(db, data.student_id)
        if not student:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Aluno não encontrado")
    if repository.get_by_slot(db, data.service_room_id, data.week_day, data.shift):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Já existe agenda para esta sala, dia e turno",
        )
    return repository.create(db, data)


@router.patch("/{service_schedule_id}", response_model=ServiceScheduleResponse)
def update_service_schedule(
    service_schedule_id: int, data: ServiceScheduleUpdate, db: Session = Depends(get_db)
):
    schedule = repository.get_by_id(db, service_schedule_id)
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

    conflict = repository.get_by_slot(db, schedule.service_room_id, new_week_day, new_shift)
    if conflict and conflict.id != schedule.id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Já existe agenda para esta sala, dia e turno",
        )

    updated = repository.update(db, service_schedule_id, data)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agenda não encontrada")
    return updated
