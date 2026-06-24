from sqlalchemy.orm import Session

from app.domains.discipline import repository
from app.domains.discipline.schemas import DisciplineUpdateRequest

def update_usecase(db: Session, data: DisciplineUpdateRequest):
    discipline = repository.update(db, data.discipline_id, data)
    return discipline
