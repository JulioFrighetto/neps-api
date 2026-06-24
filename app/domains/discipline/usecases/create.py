from sqlalchemy.orm import Session
from app.domains.discipline import repository
from app.domains.discipline.schemas import DisciplineCreate

def create_usecase(db:Session, data: DisciplineCreate):
    return repository.create(db, data)
