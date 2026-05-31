from sqlalchemy.orm import Session, selectinload

from app.core.filters import apply_filters
from app.domains.student.model import Student
from app.domains.student.schemas import StudentCreate, StudentUpdate


def get_all(db: Session, page: int = 1, per_page: int = 10, filters: dict | None = None) -> tuple[list[Student], int]:
    query = db.query(Student)
    if filters:
        query, _ = apply_filters(query, Student, filters)
    total = query.count()
    items = query.offset((page - 1) * per_page).limit(per_page).all()
    return items, total


def get_by_id(db: Session, student_id: int) -> Student | None:
    return (
        db.query(Student)
        .options(
            selectinload(Student.course),
            selectinload(Student.education_institute),
        )
        .filter(Student.id == student_id)
        .first()
    )


def get_by_course(db: Session, course_id: int, page: int = 1, per_page: int = 10, filters: dict | None = None) -> tuple[list[Student], int]:
    query = db.query(Student).filter(Student.course_id == course_id)
    if filters:
        query, _ = apply_filters(query, Student, filters)
    total = query.count()
    items = query.offset((page - 1) * per_page).limit(per_page).all()
    return items, total


def get_by_institute(db: Session, institute_id: int, page: int = 1, per_page: int = 10, filters: dict | None = None) -> tuple[list[Student], int]:
    query = db.query(Student).filter(Student.edu_institute_id == institute_id)
    if filters:
        query, _ = apply_filters(query, Student, filters)
    total = query.count()
    items = query.offset((page - 1) * per_page).limit(per_page).all()
    return items, total


def create(db: Session, data: StudentCreate) -> Student:
    student = Student(**data.model_dump())
    db.add(student)
    db.commit()
    db.refresh(student)
    return student


def update(db: Session, student_id: int, data: StudentUpdate) -> Student | None:
    student = get_by_id(db, student_id)
    if not student:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(student, field, value)
    db.commit()
    db.refresh(student)
    return student


def delete(db: Session, student_id: int) -> bool:
    student = get_by_id(db, student_id)
    if not student:
        return False
    db.delete(student)
    db.commit()
    return True
