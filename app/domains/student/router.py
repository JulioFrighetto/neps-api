import math
from datetime import date

from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.schemas import FilterInfo, Page, PaginationInfo
from app.domains.internships.model import Internship
from app.domains.student import repository
from app.domains.student.model import Student
from app.domains.student.schemas import StudentCreate, StudentUpdate

router = APIRouter(prefix="/students", tags=["Students"])

AVAILABLE_FILTERS = ["name_like", "cpf", "email_like", "discipline_id", "institution_id", "semester", "status", "internship_id"]

class StudentListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    class DisciplineSummary(BaseModel):
        model_config = ConfigDict(from_attributes=True)

        id: int
        name: str

    class InstitutionSummary(BaseModel):
        model_config = ConfigDict(from_attributes=True)

        id: int
        name: str

    class InternshipSummary(BaseModel):
        model_config = ConfigDict(from_attributes=True)

        id: int
        name: str

    id: int
    name: str | None
    cpf: str | None
    email: str | None
    phone: str | None
    course_id: int | None = None
    discipline_id: int | None
    semester: int | None
    institution_id: int
    status: str
    is_active: bool
    document_url: str
    director_signed_pdf: str | None = None
    internship_id: int | None = None
    internship_start_date: date | None = None
    internship_expected_end_date: date | None = None
    professor_name: str | None = None
    preceptor_name: str | None = None
    discipline: DisciplineSummary | None = None
    institution: InstitutionSummary | None = None
    internship: InternshipSummary | None = None

class StudentGetRequest(BaseModel):
    student_id: int
    include: str | None = None

class StudentsByDisciplineRequest(BaseModel):
    discipline_id: int
    page: int = 1
    per_page: int = 10

class StudentsByInstituteRequest(BaseModel):
    institute_id: int
    page: int = 1
    per_page: int = 10

class StudentUpdateRequest(StudentUpdate):
    student_id: int

class LinkInternshipRequest(BaseModel):
    student_id: int
    internship_id: int
    director_signed_pdf: str | None = None

def _to_response(student: Student, include: set[str] | None = None) -> StudentListResponse:
    include = include or set()

    return StudentListResponse(
        id=student.id,
        name=student.name,
        cpf=student.cpf,
        email=student.email,
        phone=student.phone,
        course_id=student.course_id,
        discipline_id=student.discipline_id,
        semester=student.semester,
        institution_id=student.edu_institute_id,
        status=student.status,
        is_active=student.is_active,
        document_url=student.document_url,
        director_signed_pdf=(
            student.director_signed_pdf.decode("utf-8")
            if isinstance(student.director_signed_pdf, bytes)
            else student.director_signed_pdf
        ),
        internship_id=student.internship_id,
        internship_start_date=student.internship_start_date,
        internship_expected_end_date=student.internship_expected_end_date,
        professor_name=student.professor_name,
        preceptor_name=student.preceptor_name,
        discipline=(
            StudentListResponse.DisciplineSummary(id=student.discipline.id, name=student.discipline.name)
            if "discipline" in include and student.discipline
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
        internship=(
            StudentListResponse.InternshipSummary(id=student.internship.id, name=student.internship.name)
            if student.internship
            else None
        ),
    )

@router.get("/", response_model=Page[StudentListResponse])
def list_students(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=500),
    name_like: str | None = Query(None),
    cpf: str | None = Query(None),
    email_like: str | None = Query(None),
    discipline_id: int | None = Query(None),
    institution_id: int | None = Query(None),
    semester: int | None = Query(None),
    student_status: str | None = Query(None, alias="status"),
    internship_id: int | None = Query(None),
    internship_id_null: bool | None = Query(None, description="Filtrar alunos sem vínculo com campo de estágio"),
    include: str | None = Query(None, description="Relacionamentos a incluir: discipline,institution"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    filters = {}
    if name_like is not None:
        filters["name_like"] = name_like
    if cpf is not None:
        digits = "".join(c for c in cpf if c.isdigit())
        if len(digits) == 11:
            filters["cpf"] = f"{digits[:3]}.{digits[3:6]}.{digits[6:9]}-{digits[9:]}"
        else:
            filters["cpf_like"] = cpf
    if email_like is not None:
        filters["email_like"] = email_like
    if discipline_id is not None:
        filters["discipline_id"] = discipline_id
    if institution_id is not None:
        filters["edu_institute_id"] = institution_id
    if semester is not None:
        filters["semester"] = semester
    if student_status is not None:
        filters["status"] = student_status
    if internship_id is not None:
        filters["internship_id"] = internship_id
    if internship_id_null is not None:
        filters["internship_id_isnull"] = internship_id_null

    include_set = {item.strip().lower() for item in include.split(",")} if include else set()

    if current_user.role == "admin":
        items, total = repository.get_all(db, page=page, per_page=per_page, filters=filters)
    elif current_user.role == "education_institute" and current_user.education_institute_id is not None:
        filters["edu_institute_id"] = current_user.education_institute_id
        items, total = repository.get_by_institute(db, current_user.education_institute_id, page=page, per_page=per_page, filters=filters)
    elif current_user.role == "internships" and current_user.internship_id is not None:
        filters["internship_id"] = current_user.internship_id
        items, total = repository.get_all(db, page=page, per_page=per_page, filters=filters)
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

@router.post("/detail", response_model=StudentListResponse)
def get_student(
    data: StudentGetRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    include_set = {"discipline", "institution"}
    if data.include:
        include_set = {item.strip().lower() for item in data.include.split(",") if item.strip()}
    student = repository.get_by_id(db, data.student_id)
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Aluno não encontrado")
    if (
        current_user.role == "education_institute"
        and student.edu_institute_id != current_user.education_institute_id
    ):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado")
    return _to_response(student, include_set)

@router.post("/by-discipline", response_model=Page[StudentListResponse])
def list_students_by_discipline(
    data: StudentsByDisciplineRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    filters = {}
    if current_user.role == "education_institute":
        filters["edu_institute_id"] = current_user.education_institute_id
    items, total = repository.get_by_discipline(db, data.discipline_id, page=data.page, per_page=data.per_page, filters=filters)
    return Page(
        items=[_to_response(item) for item in items],
        pagination=PaginationInfo(
            page=data.page,
            per_page=data.per_page,
            total=total,
            total_pages=max(1, math.ceil(total / data.per_page)) if total > 0 else 0,
        ),
    )

@router.post("/by-institute", response_model=Page[StudentListResponse])
def list_students_by_institute(
    data: StudentsByInstituteRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if (
        current_user.role == "education_institute"
        and data.institute_id != current_user.education_institute_id
    ):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado")
    items, total = repository.get_by_institute(db, data.institute_id, page=data.page, per_page=data.per_page)
    return Page(
        items=[_to_response(item) for item in items],
        pagination=PaginationInfo(
            page=data.page,
            per_page=data.per_page,
            total=total,
            total_pages=max(1, math.ceil(total / data.per_page)) if total > 0 else 0,
        ),
    )

@router.post("/", response_model=StudentListResponse, status_code=status.HTTP_201_CREATED)
def create_student(data: StudentCreate, db: Session = Depends(get_db)):
    student = repository.create(db, data)
    return _to_response(student)

@router.patch("/", response_model=StudentListResponse)
def update_student(data: StudentUpdateRequest, db: Session = Depends(get_db)):
    student = repository.update(db, data.student_id, data)
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Aluno não encontrado")
    return _to_response(student)

@router.post("/link-internship", response_model=StudentListResponse)
def link_student_to_internship(
    data: LinkInternshipRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado")
    student = repository.get_by_id(db, data.student_id)
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Aluno não encontrado")
    internship = db.query(Internship).filter(Internship.id == data.internship_id).first()
    if not internship:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campo de estágio não encontrado")
    if not internship.is_active:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Campo de estágio está inativo")
    student.internship_id = data.internship_id
    if data.director_signed_pdf is not None:
        student.director_signed_pdf = data.director_signed_pdf.encode("utf-8")
    db.commit()
    db.refresh(student)
    return _to_response(student)
