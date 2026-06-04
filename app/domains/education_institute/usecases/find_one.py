from sqlalchemy.orm import Session

from app.domains.education_institute import repository


def find_one_usecase(db: Session, institute_id: int):
    instituite = repository.get_by_id(db, institute_id)
    print("----------------------------------")
    print("repository.get_by_id(db, institute_id) --------", vars(repository.get_by_id(db, institute_id)))
    print("----------------------------------")
    return  repository.get_by_id(db, institute_id)
    
    