import math

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.schemas import FilterInfo, Page, PaginationInfo
from app.domains.student import repository
from app.domains.student.model import Student
from app.domains.student.schemas import StudentCreate, StudentUpdate

router = APIRouter(prefix="/students", tags=["Students"])

AVAILABLE_FILTERS = ["name_like", "cpf", "email_like", "course_id", "institution_id", "semester", "status"]


class StudentListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    class CourseSummary(BaseModel):
        model_config = ConfigDict(from_attributes=True)

        id: int
        name: str

    class InstitutionSummary(BaseModel):
        model_config = ConfigDict(from_attributes=True)

        id: int
        name: str

    id: int
    name: str | None
    cpf: str | None
    email: str | None
    phone: str | None
    course_id: int
    semester: int | None
    institution_id: int
    status: str
    is_active: bool
    document_url: str
    course: CourseSummary | None = None
    institution: InstitutionSummary | None = None


def _to_response(student: Student, include: set[str] | None = None) -> StudentListResponse:
    include = include or set()

    return StudentListResponse(
        id=student.id,
        name=student.name,
        cpf=student.cpf,
        email=student.email,
        phone=student.phone,
        course_id=student.course_id,
        semester=student.semester,
        institution_id=student.edu_institute_id,
        status=student.status,
        is_active=student.is_active,
        document_url=student.document_url,
        course=(
            StudentListResponse.CourseSummary(id=student.course.id, name=student.course.name)
            if "course" in include and student.course
            else None
        ),
        institution=(
            StudentListResponse.InstitutionSummary(
                id=student.education_institute.id,
                name=student.education_institute.name,
            )
            if "institution" in include and student.education_institute
            else None
        ),
    )


@router.get("/", response_model=Page[StudentListResponse])
def list_students(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    name_like: str | None = Query(None),
    cpf: str | None = Query(None),
    email_like: str | None = Query(None),
    course_id: int | None = Query(None),
    institution_id: int | None = Query(None),
    semester: int | None = Query(None),
    status: str | None = Query(None),
    include: str | None = Query(None, description="Relacionamentos a incluir: course,institution"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    filters = {}
    if name_like is not None:
        filters["name_like"] = name_like
    if cpf is not None:
        filters["cpf"] = cpf
    if email_like is not None:
        filters["email_like"] = email_like
    if course_id is not None:
        filters["course_id"] = course_id
    if institution_id is not None:
        filters["edu_institute_id"] = institution_id
    if semester is not None:
        filters["semester"] = semester
    if status is not None:
        filters["status"] = status

    include_set = {item.strip().lower() for item in include.split(",")} if include else set()

    if current_user.role == "admin":
        items, total = repository.get_all(db, page=page, per_page=per_page, filters=filters)
    elif current_user.role == "education_institute" and current_user.education_institute_id is not None:
        filters["edu_institute_id"] = current_user.education_institute_id
        items, total = repository.get_by_institute(db, current_user.education_institute_id, page=page, per_page=per_page, filters=filters)
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado")
    return Page(
        items=[_to_response(item, include_set) for item in items],
        pagination=PaginationInfo(
            page=page,
            per_page=per_page,
            total=total,
            total_pages=max(1, math.ceil(total / per_page)) if total > 0 else 0,
        ),
        filters=FilterInfo(applied=list(filters.keys()), available=AVAILABLE_FILTERS),
    )


@router.get("/{student_id}", response_model=StudentListResponse)
def get_student(
    student_id: int,
    include: str | None = Query(None, description="Relacionamentos a incluir: course,institution"),
    db: Session = Depends(get_db),
):
    include_set = {item.strip().lower() for item in include.split(",")} if include else set()
    student = repository.get_by_id(db, student_id)
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Aluno não encontrado")
    return _to_response(student, include_set)


@router.get("/by-course/{course_id}", response_model=Page[StudentListResponse])
def list_students_by_course(course_id: int, page: int = Query(1, ge=1), per_page: int = Query(10, ge=1, le=100), db: Session = Depends(get_db)):
    items, total = repository.get_by_course(db, course_id, page=page, per_page=per_page)
    return Page(
        items=[_to_response(item) for item in items],
        pagination=PaginationInfo(
            page=page,
            per_page=per_page,
            total=total,
            total_pages=max(1, math.ceil(total / per_page)) if total > 0 else 0,
        ),
    )


@router.get("/by-institute/{institute_id}", response_model=Page[StudentListResponse])
def list_students_by_institute(institute_id: int, page: int = Query(1, ge=1), per_page: int = Query(10, ge=1, le=100), db: Session = Depends(get_db)):
    items, total = repository.get_by_institute(db, institute_id, page=page, per_page=per_page)
    return Page(
        items=[_to_response(item) for item in items],
        pagination=PaginationInfo(
            page=page,
            per_page=per_page,
            total=total,
            total_pages=max(1, math.ceil(total / per_page)) if total > 0 else 0,
        ),
    )


@router.post("/", response_model=StudentListResponse, status_code=status.HTTP_201_CREATED)
def create_student(data: StudentCreate, db: Session = Depends(get_db)):
    student = repository.create(db, data)
    return _to_response(student)


@router.patch("/{student_id}", response_model=StudentListResponse)
def update_student(student_id: int, data: StudentUpdate, db: Session = Depends(get_db)):
    student = repository.update(db, student_id, data)
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Aluno não encontrado")
    return _to_response(student)
