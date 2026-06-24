from sqlalchemy.orm import Session, selectinload

from app.core.filters import apply_filters
from app.domains.course.model import Course
from app.domains.course.schemas import CourseCreate, CourseUpdate
from app.domains.discipline.model import Discipline
from app.domains.education_institute.model import EducationInstitute

def _sync_disciplines(db: Session, course: Course, items: list) -> None:
    for item in items:
        if item.id:
            disc = db.query(Discipline).filter(Discipline.id == item.id).first()
            if disc and disc not in course.disciplines:
                course.disciplines.append(disc)
        else:
            disc = Discipline(
                name=item.name,
                code=item.code,
                region_id=item.region_id,
                requires_gurney=item.requires_gurney,
            )
            db.add(disc)
            db.flush()
            course.disciplines.append(disc)

def get_all(
    db: Session,
    page: int = 1,
    per_page: int = 10,
    filters: dict | None = None,
    education_institute_id: int | None = None,
) -> tuple[list[Course], int]:
    query = db.query(Course).options(selectinload(Course.disciplines))
    if education_institute_id is not None:
        query = query.join(Course.education_institutes).filter(
            EducationInstitute.id == education_institute_id
        )
    if filters:
        query, _ = apply_filters(query, Course, filters)
    total = query.count()
    items = query.offset((page - 1) * per_page).limit(per_page).all()
    return items, total

def get_by_id(db: Session, course_id: int) -> Course | None:
    return (
        db.query(Course)
        .options(selectinload(Course.disciplines))
        .filter(Course.id == course_id)
        .first()
    )

def _sync_education_institute(db: Session, course: Course, education_institute_id: int) -> None:
    institute = db.query(EducationInstitute).filter(EducationInstitute.id == education_institute_id).first()
    if institute and institute not in course.education_institutes:
        course.education_institutes.append(institute)

def create(db: Session, data: CourseCreate) -> Course:
    values = data.model_dump(exclude={"disciplines", "education_institute_id"})
    course = Course(**values)
    db.add(course)
    db.flush()
    _sync_disciplines(db, course, data.disciplines)
    if data.education_institute_id:
        _sync_education_institute(db, course, data.education_institute_id)
    db.commit()
    db.refresh(course)
    return course

def update(db: Session, course_id: int, data: CourseUpdate) -> Course | None:
    course = get_by_id(db, course_id)
    if not course:
        return None
    values = data.model_dump(exclude_unset=True, exclude={"disciplines", "education_institute_id"})
    for field, value in values.items():
        setattr(course, field, value)
    if data.disciplines is not None:
        _sync_disciplines(db, course, data.disciplines)
    if data.education_institute_id:
        _sync_education_institute(db, course, data.education_institute_id)
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
