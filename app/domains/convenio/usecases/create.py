from sqlalchemy.orm import Session

from app.domains.convenio import repository
from app.domains.convenio.schemas import ConvenioCreate

def create_usecase(db: Session, data: ConvenioCreate):
    return repository.create(db, data)
