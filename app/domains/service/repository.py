import secrets

from sqlalchemy.orm import Session, selectinload

from app.core.security import hash_password
from app.domains.service.model import Service
from app.domains.service.schemas import ServiceCreate, ServiceUpdate
from app.domains.user.model import User


def get_all(db: Session, skip: int = 0, limit: int = 100) -> tuple[list[Service], int]:
    query = db.query(Service).options(selectinload(Service.user))
    total = query.count()
    items = query.offset(skip).limit(limit).all()
    return items, total


def get_by_id(db: Session, service_id: int) -> Service | None:
    return (
        db.query(Service)
        .options(selectinload(Service.user))
        .filter(Service.id == service_id)
        .first()
    )


def get_by_name(db: Session, name: str) -> Service | None:
    return db.query(Service).filter(Service.name == name).first()


def create(db: Session, data: ServiceCreate) -> Service:
    service = Service(
        name=data.name,
        region_id=data.region_id,
        is_active=data.is_active
    )
    db.add(service)
    db.flush()

    # Se não houver dados de usuário, apenas cria a unidade sem usuário associado.
    if data.user_email:
        temp_password = secrets.token_urlsafe(16)
        user = User(
            name=data.user_name,
            email=data.user_email,
            password=hash_password(temp_password),
            role="service",
            service_id=service.id,
            is_active=True,
        )
        db.add(user)
        db.commit()
        db.refresh(service)
        db.refresh(user)
        service.user = user
    else:
        db.commit()
        db.refresh(service)
    return service


def update(db: Session, service_id: int, data: ServiceUpdate) -> Service | None:
    service = get_by_id(db, service_id)
    if not service:
        return None

    payload = data.model_dump(exclude_unset=True)

    # Service fields
    for field in ("name", "region_id", "is_active"):
        if field in payload:
            setattr(service, field, payload[field])

    # Linked user fields
    if "user_email" in payload and not service.user:
        temp_password = secrets.token_urlsafe(16)
        user = User(
            name=payload.get("user_name") or service.name,
            email=payload["user_email"],
            password=hash_password(temp_password),
            role="service",
            service_id=service.id,
            is_active=True,
        )
        db.add(user)
        service.user = user
    elif service.user:
        if "user_name" in payload:
            service.user.name = payload["user_name"]
        if "user_email" in payload:
            service.user.email = payload["user_email"]

    db.commit()
    db.refresh(service)
    return service


def delete(db: Session, service_id: int) -> bool:
    service = get_by_id(db, service_id)
    if not service:
        return False
    db.delete(service)
    db.commit()
    return True
