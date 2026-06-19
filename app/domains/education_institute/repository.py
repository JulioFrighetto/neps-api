from sqlalchemy.orm import Session, selectinload
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status

from app.domains.education_institute.model import EducationInstitute
from app.domains.education_institute.schemas import (
    EducationInstituteCreate,
    EducationInstituteUpdate,
)
from app.domains.region.model import Region
from app.domains.user.model import User
from app.core.security import hash_password
import secrets


def get_all(db: Session, page: int = 1, per_page: int = 10, filters: dict | None = None) -> tuple[list[EducationInstitute], int]:
    query = db.query(EducationInstitute).options(
        selectinload(EducationInstitute.users),
        selectinload(EducationInstitute.regions),
        selectinload(EducationInstitute.courses),
    )
    if filters:
        from app.core.filters import apply_filters
        query, _ = apply_filters(query, EducationInstitute, filters)
    total = query.count()
    items = query.offset((page - 1) * per_page).limit(per_page).all()
    return items, total


def get_by_id(db: Session, institute_id: int) -> EducationInstitute | None:
    return (
        db.query(EducationInstitute)
        .options(
            selectinload(EducationInstitute.students),
            selectinload(EducationInstitute.users),
            selectinload(EducationInstitute.regions),
            selectinload(EducationInstitute.courses),
        )
        .filter(EducationInstitute.id == institute_id)
        .first()
    )


def create(db: Session, data: EducationInstituteCreate) -> EducationInstitute:
    payload = data.model_dump(exclude_none=True)
    region_ids = payload.pop("region_ids", None)
    user_name = payload.pop("user_name", None)
    user_email = payload.pop("user_email", None)
    institute_email = payload.get("email")
    effective_user_email = user_email or institute_email
    
    institute = EducationInstitute(**payload)
    
    if region_ids:
        regions = db.query(Region).filter(Region.id.in_(region_ids)).all()
        institute.regions = regions
    
    db.add(institute)
    db.flush()  
    
    if effective_user_email:
        temp_password = secrets.token_urlsafe(16)
        user = User(
            name=user_name or institute.name,
            email=effective_user_email,
            password=hash_password(temp_password),
            role="education_institute",
            education_institute_id=institute.id,
            is_active=True,
        )
        db.add(user)
    
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        # Assume unique constraint on users.email or institutes.email
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email já cadastrado",
        ) from exc
    return get_by_id(db, institute.id)


def update(
    db: Session, institute_id: int, data: EducationInstituteUpdate
) -> EducationInstitute | None:
    institute = get_by_id(db, institute_id)
    if not institute:
        return None
    payload = data.model_dump(exclude_unset=True)
    region_ids = payload.pop("region_ids", None)
    for field, value in payload.items():
        setattr(institute, field, value)
    if region_ids is not None:
        regions = db.query(Region).filter(Region.id.in_(region_ids)).all()
        institute.regions = regions
    db.commit()
    db.refresh(institute)
    return institute


def delete(db: Session, institute_id: int) -> bool:
    institute = get_by_id(db, institute_id)
    if not institute:
        return False
    db.delete(institute)
    db.commit()
    return True
