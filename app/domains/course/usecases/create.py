from sqlalchemy.orm import Session

from app.domains.course import repository
from app.domains.course.schemas import CourseCreate

def create_usecase(db: Session, data: CourseCreate):
    return repository.create(db, data)
