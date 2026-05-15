from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.domains.student import repository
from app.domains.student.schemas import StudentCreate, StudentResponse, StudentUpdate

router = APIRouter(prefix="/students", tags=["Students"])


@router.get("/", response_model=list[StudentResponse])
def list_students(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return repository.get_all(db, skip=skip, limit=limit)


@router.get("/{student_id}", response_model=StudentResponse)
def get_student(student_id: int, db: Session = Depends(get_db)):
    student = repository.get_by_id(db, student_id)
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Aluno não encontrado")
    return student


@router.get("/by-course/{course_id}", response_model=list[StudentResponse])
def list_students_by_course(course_id: int, db: Session = Depends(get_db)):
    return repository.get_by_course(db, course_id)


@router.get("/by-institute/{institute_id}", response_model=list[StudentResponse])
def list_students_by_institute(institute_id: int, db: Session = Depends(get_db)):
    return repository.get_by_institute(db, institute_id)


@router.post("/", response_model=StudentResponse, status_code=status.HTTP_201_CREATED)
def create_student(data: StudentCreate, db: Session = Depends(get_db)):
    return repository.create(db, data)


@router.patch("/{student_id}", response_model=StudentResponse)
def update_student(student_id: int, data: StudentUpdate, db: Session = Depends(get_db)):
    student = repository.update(db, student_id, data)
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Aluno não encontrado")
    return student


@router.delete("/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_student(student_id: int, db: Session = Depends(get_db)):
    deleted = repository.delete(db, student_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Aluno não encontrado")
