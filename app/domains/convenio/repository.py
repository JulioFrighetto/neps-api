from sqlalchemy.orm import Session, selectinload

from app.domains.convenio.constants import STATUS_FIRMADO
from app.domains.convenio.model import Convenio
from app.domains.convenio.schemas import ConvenioCreate, ConvenioUpdate
from app.domains.education_institute.schemas import EducationInstituteCreate
from app.domains.education_institute.usecases.create import (
    create_usecase as create_institute_usecase,
)

def get_all(db: Session, page: int = 1, per_page: int = 10, filters: dict | None = None) -> tuple[list[Convenio], int]:
    query = db.query(Convenio).options(selectinload(Convenio.education_institute))
    if filters:
        from app.core.filters import apply_filters
        query, _ = apply_filters(query, Convenio, filters)
    total = query.count()
    items = query.offset((page - 1) * per_page).limit(per_page).all()
    return items, total

def get_by_id(db: Session, convenio_id: int) -> Convenio | None:
    return (
        db.query(Convenio)
        .options(selectinload(Convenio.education_institute))
        .filter(Convenio.id == convenio_id)
        .first()
    )

def _firmar(
    db: Session,
    convenio: Convenio,
    *,
    region_ids: list[int] | None,
    user_name: str | None,
    user_email: str | None,
) -> None:
    """Cria a instituição de ensino vinculada com os mesmos dados do convênio firmado."""
    institute_data = EducationInstituteCreate(
        name=convenio.name,
        is_active=convenio.is_active,
        cnpj=convenio.cnpj,
        address=convenio.address,
        phone=convenio.phone,
        email=convenio.email,
        priority=convenio.priority,
        user_name=user_name,
        user_email=user_email,
        region_ids=region_ids,
    )
    institute = create_institute_usecase(db, institute_data)
    convenio.education_institute_id = institute.id

def create(db: Session, data: ConvenioCreate) -> Convenio:
    payload = data.model_dump(exclude={"user_name", "user_email", "region_ids"})
    convenio = Convenio(**payload)
    db.add(convenio)
    db.flush()

    if convenio.status == STATUS_FIRMADO:
        _firmar(db, convenio, region_ids=data.region_ids, user_name=data.user_name, user_email=data.user_email)

    db.commit()
    return get_by_id(db, convenio.id)

def update(db: Session, convenio_id: int, data: ConvenioUpdate) -> Convenio | None:
    convenio = get_by_id(db, convenio_id)
    if not convenio:
        return None

    payload = data.model_dump(exclude_unset=True)
    region_ids = payload.pop("region_ids", None)
    user_name = payload.pop("user_name", None)
    user_email = payload.pop("user_email", None)

    for field, value in payload.items():
        setattr(convenio, field, value)

    db.flush()

    if convenio.status == STATUS_FIRMADO and convenio.education_institute_id is None:
        _firmar(db, convenio, region_ids=region_ids, user_name=user_name, user_email=user_email)

    db.commit()
    return get_by_id(db, convenio_id)

def delete(db: Session, convenio_id: int) -> bool:
    convenio = get_by_id(db, convenio_id)
    if not convenio:
        return False
    db.delete(convenio)
    db.commit()
    return True
