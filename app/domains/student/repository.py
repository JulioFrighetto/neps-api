from sqlalchemy.orm import Session

from app.domains.student.model import Student
from app.domains.student.schemas import StudentCreate, StudentUpdate


def get_all(db: Session, skip: int = 0, limit: int = 100) -> list[Student]:
    return db.query(Student).offset(skip).limit(limit).all()


def get_by_id(db: Session, student_id: int) -> Student | None:
    return db.query(Student).filter(Student.id == student_id).first()


def get_by_course(db: Session, course_id: int) -> list[Student]:
    return db.query(Student).filter(Student.course_id == course_id).all()


def get_by_institution(db: Session, institution_id: int) -> list[Student]:
    return db.query(Student).filter(Student.edu_institute_id == institution_id).all()


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
