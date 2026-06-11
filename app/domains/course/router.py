import math

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.schemas import FilterInfo, Page, PaginationInfo
from app.domains.course import repository
from app.domains.course.schemas import (CourseBrief, CourseCreate,
                                        CourseFilters, CourseGetRequest,
                                        CourseResponse, CourseUpdate,
                                        CourseUpdateRequest)

router = APIRouter(prefix="/courses", tags=["Courses"])

AVAILABLE_FILTERS = ["name_like"]


def _get_page(db, page, per_page, filters):
    items, total = repository.get_all(
        db,
        page=page,
        per_page=per_page,
        filters=filters,
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
    per_page: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return _get_page(
        db,
        page=page,
        per_page=per_page,
        filters=filters.model_dump(exclude_none=True),
    )


@router.get("/list", response_model=Page[CourseBrief])
def list_courses_brief(
    filters: CourseFilters = Depends(),
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    page_obj = _get_page(
        db,
        page=page,
        per_page=per_page,
        filters=filters.model_dump(exclude_none=True),
    )
    brief_items = [{"id": d.id, "name": d.name} for d in page_obj.items]
    return Page(
        items=brief_items,
        pagination=page_obj.pagination,
        filters=page_obj.filters,
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
