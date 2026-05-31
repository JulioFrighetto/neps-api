import secrets

from sqlalchemy.orm import Session, selectinload

from app.core.security import hash_password
from app.domains.service.model import Service
from app.domains.service.schemas import ServiceCreate, ServiceUpdate
from app.domains.user.model import User


def get_all(db: Session, page: int = 1, per_page: int = 10, filters: dict | None = None) -> tuple[list[Service], int]:
    query = db.query(Service).options(selectinload(Service.users))
    if filters:
        from app.core.filters import apply_filters
        query, _ = apply_filters(query, Service, filters)
    total = query.count()
    items = query.offset((page - 1) * per_page).limit(per_page).all()
    return items, total


def get_by_id(db: Session, service_id: int) -> Service | None:
    return (
        db.query(Service)
        .options(selectinload(Service.users))
        .filter(Service.id == service_id)
        .first()
    )


def _create_service_user(
    db: Session,
    service: Service,
    *,
    email: str,
    name: str,
) -> User:
    user = User(
        name=name,
        email=email,
        password=hash_password(secrets.token_urlsafe(16)),
        role="service",
        service_id=service.id,
        is_active=True,
    )
    db.add(user)
    service.users.append(user)
    return user


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

    # Se não houver dados de usuário, apenas cria o campo de estágio sem usuário associado.
    if data.user_email:
        _create_service_user(
            db,
            service,
            email=data.user_email,
            name=data.user_name or data.name,
        )

    db.commit()
    return get_by_id(db, service.id) or service


def update(db: Session, service_id: int, data: ServiceUpdate) -> Service | None:
    service = get_by_id(db, service_id)
    if not service:
        return None

    payload = data.model_dump(exclude_unset=True)

    # Service fields
    for field in ("name", "region_id", "is_active"):
        if field in payload:
            setattr(service, field, payload[field])

    # Linked user fields now create additional users for the same field of internship.
    if "user_email" in payload and payload["user_email"]:
        _create_service_user(
            db,
            service,
            email=payload["user_email"],
            name=payload.get("user_name") or service.name,
        )

    db.commit()
    return get_by_id(db, service.id) or service


def delete(db: Session, service_id: int) -> bool:
    service = get_by_id(db, service_id)
    if not service:
        return False
    db.delete(service)
    db.commit()
    return True
