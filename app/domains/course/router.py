import math

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.schemas import FilterInfo, Page, PaginationInfo
from app.domains.course import repository
from app.domains.course.schemas import (CourseBrief, CourseCreate,
                                        CourseFilters, CourseGetRequest,
                                        CourseResponse, CourseUpdate,
                                        CourseUpdateRequest, DisciplineBrief)

router = APIRouter(prefix="/courses", tags=["Courses"])

AVAILABLE_FILTERS = ["name_like"]


def _get_page(db, page, per_page, filters, education_institute_id=None):
    items, total = repository.get_all(
        db,
        page=page,
        per_page=per_page,
        filters=filters,
        education_institute_id=education_institute_id,
    )
    return Page(
        items=items,
        pagination=PaginationInfo(
            page=page,
            per_page=per_page,
            total=total,
            total_pages=max(1, math.ceil(total / per_page))
            if total > 0 else 0,
        ),
        filters=FilterInfo(
            applied=list(filters.keys()),
            available=AVAILABLE_FILTERS,
        ),
    )


@router.get("/", response_model=Page[CourseResponse])
def list_courses(
    filters: CourseFilters = Depends(),
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if current_user.role == "internships":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado")
    education_institute_id = (
        current_user.education_institute_id if current_user.role == "education_institute" else None
    )
    return _get_page(
        db,
        page=page,
        per_page=per_page,
        filters=filters.model_dump(exclude_none=True),
        education_institute_id=education_institute_id,
    )


@router.get("/list", response_model=Page[CourseBrief])
def list_courses_brief(
    filters: CourseFilters = Depends(),
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if current_user.role == "internships":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado")
    education_institute_id = (
        current_user.education_institute_id if current_user.role == "education_institute" else None
    )
    page_obj = _get_page(
        db,
        page=page,
        per_page=per_page,
        filters=filters.model_dump(exclude_none=True),
        education_institute_id=education_institute_id,
    )
    brief_items = [{"id": d.id, "name": d.name} for d in page_obj.items]
    return Page(
        items=brief_items,
        pagination=page_obj.pagination,
        filters=page_obj.filters,
    )


@router.post("/detail", response_model=CourseResponse)
def get_course(data: CourseGetRequest, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if current_user.role == "internships":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado")
    course = repository.get_by_id(db, data.course_id)
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Curso não encontrado")
    return course


@router.post("/", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
def create_course(data: CourseCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if current_user.role not in ("admin", "education_institute"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado")
    if current_user.role != "admin":
        data.education_institute_id = current_user.education_institute_id
    return repository.create(db, data)


@router.put("/", response_model=CourseResponse)
@router.patch("/", response_model=CourseResponse)
def update_course(data: CourseUpdateRequest, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if current_user.role not in ("admin", "education_institute"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado")
    if current_user.role != "admin":
        data.education_institute_id = current_user.education_institute_id
    course = repository.update(db, data.course_id, data)
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Curso não encontrado")
    return course


class CourseDisciplineRequest(BaseModel):
    course_id: int
    discipline_id: int


@router.get("/disciplines", response_model=list[DisciplineBrief])
def list_course_disciplines(
    course_id: int = Query(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    course = repository.get_by_id(db, course_id)
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Curso não encontrado")
    return course.disciplines


@router.post("/disciplines/link", response_model=CourseResponse, status_code=status.HTTP_200_OK)
def link_discipline_to_course(data: CourseDisciplineRequest, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    from app.domains.discipline.model import Discipline
    course = repository.get_by_id(db, data.course_id)
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Curso não encontrado")
    discipline = db.query(Discipline).filter(Discipline.id == data.discipline_id).first()
    if not discipline:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Disciplina não encontrada")
    if discipline not in course.disciplines:
        course.disciplines.append(discipline)
        db.commit()
        db.refresh(course)
    return course


@router.delete("/disciplines", response_model=CourseResponse, status_code=status.HTTP_200_OK)
def unlink_discipline_from_course(data: CourseDisciplineRequest, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    from app.domains.discipline.model import Discipline
    course = repository.get_by_id(db, data.course_id)
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Curso não encontrado")
    discipline = db.query(Discipline).filter(Discipline.id == data.discipline_id).first()
    if not discipline:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Disciplina não encontrada")
    if discipline in course.disciplines:
        course.disciplines.remove(discipline)
        db.commit()
        db.refresh(course)
    return course
