from sqlalchemy.orm import Session

from app.domains.convenio import repository
from app.domains.convenio.schemas import ConvenioUpdate

def update_usecase(db: Session, convenio_id: int, data: ConvenioUpdate):
    return repository.update(db, convenio_id, data)
