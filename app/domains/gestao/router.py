import math

from fastapi import APIRouter, Body, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session, selectinload

from app.core.database import get_db
from app.core.filters import apply_filters
from app.core.schemas import FilterInfo, Page, PaginationInfo
from app.domains.student.model import Student

router = APIRouter(prefix="/", tags=["Gestão"])


class GestaoStudentCreate(BaseModel):
    name: str
    cpf: str | None = None
    email: str | None = None
    phone: str | None = None
    discipline_id: int
    semester: int | None = None
    institution_id: int


class GestaoStudentUpdate(BaseModel):
    name: str | None = None
    cpf: str | None = None
    email: str | None = None
    phone: str | None = None
    discipline_id: int | None = None
    semester: int | None = None
    institution_id: int | None = None


class GestaoStudentGetRequest(BaseModel):
    student_id: int
    include: str | None = None


class GestaoStudentUpdateRequest(GestaoStudentUpdate):
    student_id: int


class GestaoStudentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    class DisciplineSummary(BaseModel):
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
    discipline_id: int
    semester: int | None
    institution_id: int
    discipline: DisciplineSummary | None = None
    institution: InstitutionSummary | None = None


AVAILABLE_FILTERS = ["name_like", "cpf", "email", "discipline_id", "institution_id", "semester"]


def _to_response(student: Student, include: set[str] | None = None) -> GestaoStudentResponse:
    include = include or set()

    return GestaoStudentResponse(
        id=student.id,
        name=student.name,
        cpf=student.cpf,
        email=student.email,
        phone=student.phone,
        discipline_id=student.discipline_id,
        semester=student.semester,
        institution_id=student.edu_institute_id,
        discipline=(
            GestaoStudentResponse.DisciplineSummary(id=student.discipline.id, name=student.discipline.name)
            if "discipline" in include and student.discipline
            else None
        ),
        institution=(
            GestaoStudentResponse.InstitutionSummary(
                id=student.education_institute.id,
                name=student.education_institute.name,
            )
            if "institution" in include and student.education_institute
            else None
        ),
    )


@router.get("/students", response_model=Page[GestaoStudentResponse])
def list_students(
    page: int = Body(1, ge=1),
    per_page: int = Body(10, ge=1, le=100),
    name_like: str | None = Body(None),
    cpf: str | None = Body(None),
    email: str | None = Body(None),
    discipline_id: int | None = Body(None),
    institution_id: int | None = Body(None),
    semester: int | None = Body(None),
    include: str | None = Body(None, description="Relacionamentos a incluir: discipline,institution"),
    db: Session = Depends(get_db),
):
    filters = {}
    if name_like is not None:
        filters["name_like"] = name_like
    if cpf is not None:
        filters["cpf"] = cpf
    if email is not None:
        filters["email"] = email
    if discipline_id is not None:
        filters["discipline_id"] = discipline_id
    if institution_id is not None:
        filters["edu_institute_id"] = institution_id
    if semester is not None:
        filters["semester"] = semester

    include_set = {item.strip().lower() for item in include.split(",")} if include else set()

    query = db.query(Student)
    if "discipline" in include_set:
        query = query.options(selectinload(Student.discipline))
    if "institution" in include_set:
        query = query.options(selectinload(Student.education_institute))

    if filters:
        query, _ = apply_filters(query, Student, filters)
    total = query.count()
    items = query.offset((page - 1) * per_page).limit(per_page).all()

    return Page(
        items=[_to_response(s, include_set) for s in items],
        pagination=PaginationInfo(
            page=page,
            per_page=per_page,
            total=total,
            total_pages=max(1, math.ceil(total / per_page)) if total > 0 else 0,
        ),
        filters=FilterInfo(applied=list(filters.keys()), available=AVAILABLE_FILTERS),
    )


@router.post("/students/detail", response_model=GestaoStudentResponse)
def get_student(data: GestaoStudentGetRequest, db: Session = Depends(get_db)):
    include_set = {item.strip().lower() for item in data.include.split(",")} if data.include else set()

    query = db.query(Student)
    if "discipline" in include_set:
        query = query.options(selectinload(Student.discipline))
    if "institution" in include_set:
        query = query.options(selectinload(Student.education_institute))

    student = query.filter(Student.id == data.student_id).first()
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Aluno não encontrado")
    return _to_response(student, include_set)


@router.post("/students", response_model=GestaoStudentResponse, status_code=status.HTTP_201_CREATED)
def create_student(data: GestaoStudentCreate, db: Session = Depends(get_db)):
    student = Student(
        name=data.name,
        cpf=data.cpf,
        email=data.email,
        phone=data.phone,
        discipline_id=data.discipline_id,
        semester=data.semester,
        edu_institute_id=data.institution_id,
        status="PENDING",
        is_active=True,
    )
    db.add(student)
    db.commit()
    db.refresh(student)
    return _to_response(student)


@router.put("/students", response_model=GestaoStudentResponse)
@router.patch("/students", response_model=GestaoStudentResponse)
def update_student(data: GestaoStudentUpdateRequest, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.id == data.student_id).first()
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Aluno não encontrado")

    update_data = data.model_dump(exclude_unset=True)
    field_map = {"institution_id": "edu_institute_id"}
    for key, value in update_data.items():
        col = field_map.get(key, key)
        setattr(student, col, value)

    db.commit()
    db.refresh(student)
    return _to_response(student)
