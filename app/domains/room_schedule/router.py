from typing import Literal

from fastapi import APIRouter, Body, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.domains.period import repository as period_repository
from app.domains.room.repository import get_by_id as get_room_by_id
from app.domains.room_schedule import repository_nested as schedule_repository

router = APIRouter(prefix="/rooms", tags=["Room Schedules"])

DayOfWeek = Literal["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY", "SUNDAY"]
PeriodName = Literal["MORNING", "AFTERNOON", "EVENING"]


class AssignStudentToPeriodRequest(BaseModel):
    room_id: int
    day_of_week: DayOfWeek
    period: PeriodName
    period_id: int
    student_id: int


class GetRoomScheduleRequest(BaseModel):
    room_id: int


class AvailableSlotsRequest(BaseModel):
    student_id: int
    room_id: int | None = None


@router.post("/schedule", response_model=dict)
def get_room_schedule(payload: GetRoomScheduleRequest, db: Session = Depends(get_db)):
    room = get_room_by_id(db, payload.room_id)
    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sala não encontrada")

    schedule = schedule_repository.create_schedule_for_room(db, payload.room_id)

    result_days = []
    for day in schedule.days:
        periods = []
        for period in day.periods:
            periods.append(
                {
                    "period": period.period,
                    "studentIds": [student.id for student in period.students],
                }
            )
        result_days.append(
            {
                "dayOfWeek": day.day_of_week,
                "periods": periods,
            }
        )

    return {
        "roomId": payload.room_id,
        "days": result_days,
    }


@router.post("/schedule/student", response_model=dict, status_code=status.HTTP_200_OK)
def assign_student_to_period(
    payload: AssignStudentToPeriodRequest,
    db: Session = Depends(get_db),
):
    room = get_room_by_id(db, payload.room_id)
    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sala não encontrada")

    period_model = period_repository.get_by_id(db, payload.period_id)
    if not period_model:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Período não encontrado")

    try:
        updated_period = schedule_repository.assign_student_to_period(
            db=db,
            room_id=payload.room_id,
            day_of_week=payload.day_of_week,
            period_name=payload.period,
            period_id=payload.period_id,
            student_id=payload.student_id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))

    if not updated_period:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Período ou aluno não encontrado")

    return {
        "roomId": payload.room_id,
        "dayOfWeek": payload.day_of_week,
        "period": payload.period,
        "studentIds": [student.id for student in updated_period.students],
    }


@router.delete("/schedule/student", status_code=status.HTTP_200_OK)
def remove_student_from_period(
    payload: AssignStudentToPeriodRequest,
    db: Session = Depends(get_db),
):
    room = get_room_by_id(db, payload.room_id)
    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sala não encontrada")

    period_model = period_repository.get_by_id(db, payload.period_id)
    if not period_model:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Período não encontrado")

    updated_period = schedule_repository.remove_student_from_period(
        db=db,
        room_id=payload.room_id,
        day_of_week=payload.day_of_week,
        period_name=payload.period,
        period_id=payload.period_id,
        student_id=payload.student_id,
    )

    if not updated_period:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Aluno não encontrado neste horário")

    return {
        "roomId": payload.room_id,
        "dayOfWeek": payload.day_of_week,
        "period": payload.period,
        "studentIds": [student.id for student in updated_period.students],
    }


@router.post("/available-slots", response_model=list[dict])
def available_slots_for_student(payload: AvailableSlotsRequest, db: Session = Depends(get_db)):
    """Return available slots for a given student across rooms (or single room if `room_id` provided)."""
    slots = schedule_repository.get_available_slots_for_student(
        db,
        payload.student_id,
        room_id=payload.room_id,
    )
    return slots
