from sqlalchemy.orm import Session
from app.domains.education_institute import repository
from app.domains.education_institute.schemas import EducationInstituteUpdate


def update_usecase(db: Session, institute_id: int, data: EducationInstituteUpdate):
    institute = repository.get_by_id(db, institute_id)
    print("institute", vars(institute))
    update=repository.update(db, institute_id, data)
    print("update", vars(update))
    return update
