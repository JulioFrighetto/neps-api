import math

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.schemas import FilterInfo, Page, PaginationInfo
from app.domains.period import repository
from app.domains.period.schemas import (
    PeriodCreate,
    PeriodResponse,
    PeriodUpdate,
    PeriodDetailResponse,
    StudentLinkRequest,
    StudentSummary,
)
from app.domains.student import repository as student_repository
from app.domains.student.model import Student

router = APIRouter(prefix="/periods", tags=["Periods"])

AVAILABLE_FILTERS = ["name_like", "is_active", "start_date_from", "start_date_to", "end_date_from", "end_date_to"]


class PeriodDetailRequest(BaseModel):
    period_id: int
    include: str | None = None


class PeriodStudentLinkRequest(StudentLinkRequest):
    period_id: int


class PeriodUpdateRequest(PeriodUpdate):
    period_id: int


@router.get("/", response_model=Page[PeriodResponse])
def list_periods(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    name_like: str | None = Query(None),
    is_active: bool | None = Query(None),
    start_date_from: str | None = Query(None),
    start_date_to: str | None = Query(None),
    end_date_from: str | None = Query(None),
    end_date_to: str | None = Query(None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    filters = {k: v for k, v in {
        "name_like": name_like,
        "is_active": is_active,
        "start_date_from": start_date_from,
        "start_date_to": start_date_to,
        "end_date_from": end_date_from,
        "end_date_to": end_date_to,
    }.items() if v is not None}

    institute_priority = None
    if current_user.role == "education_institute":
        if current_user.education_institute_id is None or current_user.education_institute is None:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado")
        institute_priority = current_user.education_institute.priority
    elif current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado")

    items, total = repository.get_all(
        db,
        page=page,
        per_page=per_page,
        filters=filters,
        institute_priority=institute_priority,
    )
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


@router.post("/detail", response_model=PeriodDetailResponse)
def get_period(
    data: PeriodDetailRequest,
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

    inc = {p.strip().lower() for p in data.include.split(",")} if data.include else set()

    if "students" in inc:
        period = repository.get_by_id_with_students(db, data.period_id, institute_priority=institute_priority)
    else:
        period = repository.get_by_id(db, data.period_id, institute_priority=institute_priority)

    if not period:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Período não encontrado")

    # Build response dict
    base = {
        "id": period.id,
        "name": period.name,
        "priority_start_date": period.priority_start_date,
        "priority_end_date": period.priority_end_date,
        "start_date": period.start_date,
        "end_date": period.end_date,
        "is_active": period.is_active,
        "created_at": getattr(period, "created_at", None),
        "updated_at": getattr(period, "updated_at", None),
    }
    students_list: list[dict] = []
    student_ids: list[int] = []
    if "students" in inc:
        from app.domains.room_schedule.models_nested import SchedulePeriod, ScheduleDay, Schedule
        from app.domains.room_schedule.models_nested import schedule_period_students
        from app.domains.room.model import Room
        
        from app.domains.education_institute.model import EducationInstitute
        student_query = db.query(Student).options(
            selectinload(Student.discipline),
            selectinload(Student.education_institute).selectinload(EducationInstitute.regions),
        )

        if current_user.role != "admin":
            student_query = student_query.filter(Student.edu_institute_id == current_user.education_institute_id)

        student_query = student_query.filter(Student.is_active.is_(True))

        for s in student_query.all():
            # Check if student has a slot assigned (schedule)
            slot_query = (
                db.query(SchedulePeriod, ScheduleDay, Schedule)
                .outerjoin(ScheduleDay, SchedulePeriod.schedule_day_id == ScheduleDay.id)
                .outerjoin(Schedule, ScheduleDay.schedule_id == Schedule.id)
                .outerjoin(schedule_period_students, schedule_period_students.c.schedule_period_id == SchedulePeriod.id)
                .filter(schedule_period_students.c.student_id == s.id)
                .first()
            )
            slot_obj = None
            has_slot = False
            if slot_query:
                schedule_period, schedule_day, schedule = slot_query
                # only consider a slot if a schedule (and its room) exists
                if schedule is not None:
                    has_slot = True
                    room = db.query(Room).filter(Room.id == schedule.room_id).first()
                    slot_obj = {
                        "room_id": schedule.room_id,
                        "room_name": room.name if room else None,
                        "day_of_week": schedule_day.day_of_week,
                        "period": schedule_period.period,
                    }
            
            students_list.append(
                {
                    "id": s.id,
                    "name": s.name,
                    "cpf": s.cpf,
                    "semester": s.semester,
                    "has_slot": has_slot,
                    "slot": slot_obj,
                    "discipline": {"id": s.discipline.id, "name": s.discipline.name} if getattr(s, "discipline", None) else None,
                    "institution": {
                        "id": s.education_institute.id,
                        "name": s.education_institute.name,
                        "region_id": s.education_institute.regions[0].id if s.education_institute.regions else None,
                    } if getattr(s, "education_institute", None) else None,
                }
            )
            student_ids.append(s.id)

    base["students"] = students_list
    base["student_ids"] = student_ids

    return PeriodDetailResponse(**base)



@router.post("/students", status_code=status.HTTP_201_CREATED)
def link_student_to_period(
    data: PeriodStudentLinkRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    # permission
    if current_user.role != "education_institute":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado")
    if current_user.education_institute_id is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado")

    # validate period visibility
    period = repository.get_by_id(db, data.period_id, institute_priority=current_user.education_institute.priority)
    if not period:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Período não encontrado ou não visível")

    # validate student
    student = student_repository.get_by_id(db, data.student_id)
    if not student or not student.is_active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Aluno não encontrado ou inativo")
    if student.edu_institute_id != current_user.education_institute_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Aluno não pertence à instituição")

    # check already linked
    if any(s.id == student.id for s in getattr(period, "students", [])):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Aluno já está vinculado ao período")

    try:
        repository.link_student(db, data.period_id, student)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    return {"message": "Aluno vinculado com sucesso"}


@router.delete("/students", status_code=status.HTTP_200_OK)
def unlink_student_from_period(
    data: PeriodStudentLinkRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    institute_priority = None
    if current_user.role == "education_institute":
        if current_user.education_institute_id is None:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado")
        institute = current_user.education_institute or db.query(
            __import__("app.domains.education_institute.model", fromlist=["EducationInstitute"]).EducationInstitute
        ).filter_by(id=current_user.education_institute_id).first()
        if not institute:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado")
        institute_priority = institute.priority
    elif current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado")

    period = repository.get_by_id_with_students(db, data.period_id, institute_priority=institute_priority)
    if not period:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Período não encontrado ou não visível")

    student = student_repository.get_by_id(db, data.student_id)
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Aluno não encontrado")
    if (
        current_user.role == "education_institute"
        and student.edu_institute_id != current_user.education_institute_id
    ):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Aluno não pertence à instituição")

    is_linked_to_period = any(s.id == student.id for s in getattr(period, "students", []))
    if is_linked_to_period:
        try:
            repository.unlink_student(db, data.period_id, student)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    from app.domains.room_schedule import repository_nested as schedule_repository

    schedule_repository.remove_student_from_all_periods(db, student.id)

    return {"message": "Aluno desvinculado com sucesso"}


@router.post("/", response_model=PeriodResponse, status_code=status.HTTP_201_CREATED)
def create_period(data: PeriodCreate, db: Session = Depends(get_db)):
    return repository.create(db, data)


@router.patch("/", response_model=PeriodResponse)
def update_period(data: PeriodUpdateRequest, db: Session = Depends(get_db)):
    period = repository.update(db, data.period_id, data)
    if not period:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Período não encontrado")
    return period
