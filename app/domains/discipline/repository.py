from sqlalchemy.orm import Session, selectinload

from app.core.filters import apply_filters
from app.domains.discipline.model import Discipline
from app.domains.discipline.schemas import DisciplineCreate, DisciplineUpdate

def get_all(db: Session, page: int = 1, per_page: int = 10, filters: dict | None = None) -> tuple[list[Discipline], int]:
    query = db.query(Discipline).options(selectinload(Discipline.region))
    if filters:
        query, _ = apply_filters(query, Discipline, filters)
    total = query.count()
    items = query.offset((page - 1) * per_page).limit(per_page).all()
    return items, total

def get_by_id(db: Session, discipline_id: int) -> Discipline | None:
    return db.query(Discipline).options(selectinload(Discipline.region)).filter(Discipline.id == discipline_id).first()

def create(db: Session, data: DisciplineCreate) -> Discipline:
    discipline = Discipline(**data.model_dump())
    db.add(discipline)
    db.commit()
    db.refresh(discipline)
    return discipline

def update(db: Session, discipline_id: int, data: DisciplineUpdate) -> Discipline | None:
    discipline = get_by_id(db, discipline_id)
    if not discipline:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(discipline, field, value)
    db.commit()
    db.refresh(discipline)
    return discipline

def delete(db: Session, discipline_id: int) -> bool:
    discipline = get_by_id(db, discipline_id)
    if not discipline:
        return False
    db.delete(discipline)
    db.commit()
    return True
