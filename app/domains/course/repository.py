from sqlalchemy.orm import Session

from app.domains.course.model import Course
from app.domains.course.schemas import CourseCreate, CourseUpdate


def get_all(db: Session, skip: int = 0, limit: int = 100) -> tuple[list[Course], int]:
    query = db.query(Course)
    total = query.count()
    items = query.offset(skip).limit(limit).all()
    return items, total


def get_by_id(db: Session, course_id: int) -> Course | None:
    return db.query(Course).filter(Course.id == course_id).first()


def create(db: Session, data: CourseCreate) -> Course:
    course = Course(**data.model_dump())
    db.add(course)
    db.commit()
    db.refresh(course)
    return course


def update(db: Session, course_id: int, data: CourseUpdate) -> Course | None:
    course = get_by_id(db, course_id)
    if not course:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(course, field, value)
    db.commit()
    db.refresh(course)
    return course


def delete(db: Session, course_id: int) -> bool:
    course = get_by_id(db, course_id)
    if not course:
        return False
    db.delete(course)
    db.commit()
    return True
