from sqlalchemy.orm import Session

from app.domains.convenio import repository

def find_one_usecase(db: Session, convenio_id: int):
    return repository.get_by_id(db, convenio_id)
