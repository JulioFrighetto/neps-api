import math

from fastapi import APIRouter, Depends, HTTPException, Body, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.schemas import Page, PaginationInfo
from app.domains.history import repository
from app.domains.history.schemas import HistoryResponse
from app.domains.student.repository import get_by_id as get_student_by_id
from app.domains.period import repository as period_repository
from app.domains.room.repository import get_by_id as get_room_by_id

router = APIRouter(prefix="/histories", tags=["Histories"])


class HistoryFilterRequest(BaseModel):
    id: int
    page: int = 1
    per_page: int = 10


def _to_response(history) -> HistoryResponse:
    if history.created_at is None or history.updated_at is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Histórico inválido: timestamps ausentes no banco",
        )

    return HistoryResponse(
        id=history.id,
        period_id=history.period_id,
        student_id=history.student_id,
        schedule_id=history.schedule_id,
        room_id=history.room_id,
        start_date=history.start_date,
        end_date=history.end_date,
        created_at=history.created_at,
        updated_at=history.updated_at,
        student=history.student,
        period=history.period,
    )


@router.post("/by-period", response_model=Page[HistoryResponse])
def list_histories_by_period(
    data: HistoryFilterRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    institute_priority = None
    if current_user.role == "education_institute":
        if current_user.education_institute_id is None or current_user.education_institute is None:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado")
        institute_priority = current_user.education_institute.priority
    elif current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado")

    period = period_repository.get_by_id(db, data.id, institute_priority=institute_priority)
    if not period:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Período não encontrado")

    items, total = repository.get_by_period(db, data.id, page=data.page, per_page=data.per_page)
    return Page(
        items=[_to_response(item) for item in items],
        pagination=PaginationInfo(
            page=data.page,
            per_page=data.per_page,
            total=total,
            total_pages=max(1, math.ceil(total / data.per_page)) if total > 0 else 0,
        ),
    )


@router.post("/by-room", response_model=Page[HistoryResponse])
def list_histories_by_room(
    data: HistoryFilterRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    room = get_room_by_id(db, data.id)
    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sala não encontrada")

    if current_user.role == "internships":
        if current_user.internship_id is None or current_user.internship_id != room.internship_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado")
    elif current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado")

    items, total = repository.get_by_room(db, data.id, page=data.page, per_page=data.per_page)
    return Page(
        items=[_to_response(item) for item in items],
        pagination=PaginationInfo(
            page=data.page,
            per_page=data.per_page,
            total=total,
            total_pages=max(1, math.ceil(total / data.per_page)) if total > 0 else 0,
        ),
    )


@router.post("/by-schedule", response_model=Page[HistoryResponse])
def list_histories_by_schedule(
    data: HistoryFilterRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    from app.domains.room_schedule.repository_nested import get_by_id as get_schedule_by_id

    schedule = get_schedule_by_id(db, data.id)
    if not schedule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Schedule não encontrado")

    room = get_room_by_id(db, schedule.room_id)
    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sala não encontrada")

    if current_user.role == "internships":
        if current_user.internship_id is None or current_user.internship_id != room.internship_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado")
    elif current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado")

    items, total = repository.get_by_schedule(db, data.id, page=data.page, per_page=data.per_page)
    return Page(
        items=[_to_response(item) for item in items],
        pagination=PaginationInfo(
            page=data.page,
            per_page=data.per_page,
            total=total,
            total_pages=max(1, math.ceil(total / data.per_page)) if total > 0 else 0,
        ),
    )


@router.post("/by-student", response_model=Page[HistoryResponse])
def list_histories_by_student(
    data: HistoryFilterRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    student = get_student_by_id(db, data.id)
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Aluno não encontrado")

    if current_user.role == "education_institute":
        if current_user.education_institute_id is None or current_user.education_institute_id != student.edu_institute_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado")
    elif current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado")

    items, total = repository.get_by_student(db, data.id, page=data.page, per_page=data.per_page)
    return Page(
        items=[_to_response(item) for item in items],
        pagination=PaginationInfo(
            page=data.page,
            per_page=data.per_page,
            total=total,
            total_pages=max(1, math.ceil(total / data.per_page)) if total > 0 else 0,
        ),
    )
