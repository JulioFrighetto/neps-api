from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.schemas import Page
from app.domains.student import repository
from app.domains.student.schemas import StudentCreate, StudentResponse, StudentUpdate

router = APIRouter(prefix="/students", tags=["Students"])


@router.get("/", response_model=Page[StudentResponse])
def list_students(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if current_user.role == "admin":
        items, total = repository.get_all(db, skip=skip, limit=limit)
    elif current_user.role == "education_institute" and current_user.education_institute_id is not None:
        items, total = repository.get_by_institute(db, current_user.education_institute_id, skip=skip, limit=limit)
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado")
    return Page(items=items, total=total, skip=skip, limit=limit, has_next=skip + limit < total)


@router.get("/{student_id}", response_model=StudentResponse)
def get_student(student_id: int, db: Session = Depends(get_db)):
    student = repository.get_by_id(db, student_id)
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Aluno não encontrado")
    return student


@router.get("/by-course/{course_id}", response_model=Page[StudentResponse])
def list_students_by_course(course_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items, total = repository.get_by_course(db, course_id, skip=skip, limit=limit)
    return Page(items=items, total=total, skip=skip, limit=limit, has_next=skip + limit < total)


@router.get("/by-institute/{institute_id}", response_model=Page[StudentResponse])
def list_students_by_institute(institute_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items, total = repository.get_by_institute(db, institute_id, skip=skip, limit=limit)
    return Page(items=items, total=total, skip=skip, limit=limit, has_next=skip + limit < total)


@router.post("/", response_model=StudentResponse, status_code=status.HTTP_201_CREATED)
def create_student(data: StudentCreate, db: Session = Depends(get_db)):
    return repository.create(db, data)


@router.patch("/{student_id}", response_model=StudentResponse)
def update_student(student_id: int, data: StudentUpdate, db: Session = Depends(get_db)):
    student = repository.update(db, student_id, data)
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Aluno não encontrado")
    return student
