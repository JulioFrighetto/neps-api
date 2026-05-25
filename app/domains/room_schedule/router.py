from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.domains.room.repository import get_by_id as get_room_by_id
from app.domains.room_schedule import repository_nested as schedule_repository

router = APIRouter(prefix="/rooms", tags=["Room Schedules"])

DayOfWeek = Literal["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY", "SUNDAY"]
PeriodName = Literal["MORNING", "AFTERNOON", "EVENING"]


class AssignStudentToPeriodRequest(BaseModel):
    student_id: int


@router.get("/{room_id}/schedule", response_model=dict)
def get_room_schedule(room_id: int, db: Session = Depends(get_db)):
    room = get_room_by_id(db, room_id)
    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sala não encontrada")

    schedule = schedule_repository.create_schedule_for_room(db, room_id)

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
        "roomId": room_id,
        "days": result_days,
    }


@router.post("/{room_id}/schedule/{day_of_week}/{period}/student", response_model=dict, status_code=status.HTTP_200_OK)
def assign_student_to_period(
    room_id: int,
    day_of_week: DayOfWeek,
    period: PeriodName,
    payload: AssignStudentToPeriodRequest,
    db: Session = Depends(get_db),
):
    room = get_room_by_id(db, room_id)
    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sala não encontrada")

    try:
        updated_period = schedule_repository.assign_student_to_period(
            db=db,
            room_id=room_id,
            day_of_week=day_of_week,
            period_name=period,
            student_id=payload.student_id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))

    if not updated_period:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Período ou aluno não encontrado")

    return {
        "roomId": room_id,
        "dayOfWeek": day_of_week,
        "period": period,
        "studentIds": [student.id for student in updated_period.students],
    }


@router.delete("/{room_id}/schedule/{day_of_week}/{period}/student", status_code=status.HTTP_200_OK)
def remove_student_from_period(
    room_id: int,
    day_of_week: DayOfWeek,
    period: PeriodName,
    payload: AssignStudentToPeriodRequest,
    db: Session = Depends(get_db),
):
    room = get_room_by_id(db, room_id)
    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sala não encontrada")

    updated_period = schedule_repository.remove_student_from_period(
        db=db,
        room_id=room_id,
        day_of_week=day_of_week,
        period_name=period,
        student_id=payload.student_id,
    )

    if not updated_period:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Aluno não encontrado neste horário")

    return {
        "roomId": room_id,
        "dayOfWeek": day_of_week,
        "period": period,
        "studentIds": [student.id for student in updated_period.students],
    }
