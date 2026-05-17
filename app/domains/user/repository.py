from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.domains.user.model import User
from app.domains.user.schemas import UserCreate, UserUpdate


def get_all(db: Session, skip: int = 0, limit: int = 100) -> list[User]:
    return db.query(User).offset(skip).limit(limit).all()


def get_by_id(db: Session, user_id: int) -> User | None:
    return db.query(User).filter(User.id == user_id).first()


def get_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()


def create(db: Session, data: UserCreate) -> User:
    user = User(
        name=data.name,
        email=data.email,
        password=hash_password(data.password),
        is_active=data.is_active,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update(db: Session, user_id: int, data: UserUpdate) -> User | None:
    user = get_by_id(db, user_id)
    if not user:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(user, field, value)
    db.commit()
    db.refresh(user)
    return user


def change_password(
    db: Session, user_id: int, current_password: str, new_password: str
) -> User | None:
    """Returns updated user, or None if current_password is wrong."""
    user = get_by_id(db, user_id)
    if not user or not verify_password(current_password, user.password):
        return None
    user.password = hash_password(new_password)
    db.commit()
    db.refresh(user)
    return user


def reset_password(db: Session, user_id: int, new_password: str) -> User | None:
    user = get_by_id(db, user_id)
    if not user:
        return None
    user.password = hash_password(new_password)
    db.commit()
    db.refresh(user)
    return user


def has_email(db: Session, email: str) -> bool:
    return get_by_email(db, email) is not None


def delete(db: Session, user_id: int) -> bool:
    user = get_by_id(db, user_id)
    if not user:
        return False
    db.delete(user)
    db.commit()
    return True


def authenticate(db: Session, email: str, password: str) -> User | None:
    user = get_by_email(db, email)
    if not user or not user.is_active:
        return None
    if not verify_password(password, user.password):
        return None
    return user
