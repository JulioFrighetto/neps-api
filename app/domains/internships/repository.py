import secrets

from sqlalchemy.orm import Session, selectinload

from app.core.security import hash_password
from app.domains.internships.model import Internship
from app.domains.internships.schemas import InternshipsCreate, InternshipsUpdate
from app.domains.user.model import User

def get_all(db: Session, page: int = 1, per_page: int = 10, filters: dict | None = None) -> tuple[list[Internship], int]:
    query = db.query(Internship).options(selectinload(Internship.users))
    if filters:
        from app.core.filters import apply_filters
        query, _ = apply_filters(query, Internship, filters)
    total = query.count()
    items = query.offset((page - 1) * per_page).limit(per_page).all()
    return items, total

def get_by_id(db: Session, internship_id: int) -> Internship | None:
    return (
        db.query(Internship)
        .options(selectinload(Internship.users))
        .filter(Internship.id == internship_id)
        .first()
    )

def _create_internships_user(
    db: Session,
    internships: Internship,
    *,
    email: str,
    name: str,
) -> User:
    user = User(
        name=name,
        email=email,
        password=hash_password(secrets.token_urlsafe(16)),
        role="internships",
        internship_id=internships.id,
        is_active=True,
    )
    db.add(user)
    internships.users.append(user)
    return user

def get_by_name(db: Session, name: str) -> Internship | None:
    return db.query(Internship).filter(Internship.name == name).first()

def create(db: Session, data: InternshipsCreate) -> Internship:
    internships = Internship(
        name=data.name,
        region_id=data.region_id,
        is_active=data.is_active
    )
    db.add(internships)
    db.flush()

    if data.user_email:
        _create_internships_user(
            db,
            internships,
            email=data.user_email,
            name=data.user_name or data.name,
        )

    db.commit()
    return get_by_id(db, internships.id) or internships

def update(db: Session, internship_id: int, data: InternshipsUpdate) -> Internship | None:
    internships = get_by_id(db, internship_id)
    if not internships:
        return None

    payload = data.model_dump(exclude_unset=True)

    for field in ("name", "region_id", "is_active"):
        if field in payload:
            setattr(internships, field, payload[field])

    if "user_email" in payload and payload["user_email"] and payload["user_email"] != (internships.users[0].email if internships.users else None):
        _create_internships_user(
            db,
            internships,
            email=payload["user_email"],
            name=payload.get("user_name") or internships.name,
        )

    db.commit()
    return get_by_id(db, internships.id) or internships

def delete(db: Session, internship_id: int) -> bool:
    internships = get_by_id(db, internship_id)
    if not internships:
        return False
    db.delete(internships)
    db.commit()
    return True
