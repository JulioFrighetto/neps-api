import math

from fastapi import APIRouter, Depends, HTTPException, Body, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.schemas import FilterInfo, Page, PaginationInfo
from app.domains.course import repository
from app.domains.course.schemas import CourseCreate, CourseResponse, CourseUpdate

router = APIRouter(prefix="/courses", tags=["Courses"])

AVAILABLE_FILTERS = ["name_like", "code_like", "region_id"]


class CourseGetRequest(BaseModel):
    course_id: int


class CourseUpdateRequest(CourseUpdate):
    course_id: int


@router.get("/", response_model=Page[CourseResponse])
def list_courses(
    page: int = Body(1, ge=1),
    per_page: int = Body(10, ge=1, le=100),
    name_like: str | None = Body(None),
    code_like: str | None = Body(None),
    region_id: int | None = Body(None),
    db: Session = Depends(get_db),
):
    filters = {k: v for k, v in {"name_like": name_like, "code_like": code_like, "region_id": region_id}.items() if v is not None}
    items, total = repository.get_all(db, page=page, per_page=per_page, filters=filters)
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


@router.post("/detail", response_model=CourseResponse)
def get_course(data: CourseGetRequest, db: Session = Depends(get_db)):
    course = repository.get_by_id(db, data.course_id)
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Curso não encontrado")
    return course


@router.post("/", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
def create_course(data: CourseCreate, db: Session = Depends(get_db)):
    return repository.create(db, data)


@router.put("/", response_model=CourseResponse)
@router.patch("/", response_model=CourseResponse)
def update_course(data: CourseUpdateRequest, db: Session = Depends(get_db)):
    course = repository.update(db, data.course_id, data)
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Curso não encontrado")
    return course
