from sqlalchemy.orm import Session

from app.domains.course import repository
from app.domains.course.schemas import CourseUpdateRequest

def update_usecase(db: Session, data: CourseUpdateRequest):
    course = repository.update(db, data.course_id, data)
    return course
