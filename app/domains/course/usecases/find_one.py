from sqlalchemy.orm import Session

from app.domains.course import repository


def find_one_usecase(db: Session, id: int):
    return repository.get_by_id(db, id)
