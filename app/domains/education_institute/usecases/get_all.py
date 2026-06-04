from sqlalchemy.orm import Session
import math
from app.core.schemas import FilterInfo, Page, PaginationInfo
from app.domains.education_institute import repository
from app.domains.education_institute.constants import AVAILABLE_FILTERS


def get_all_usecase(db: Session, page: int, per_page: int, filters: dict, current_user):
    if current_user.role == "admin":
        items, total = repository.get_all(db, page=page, per_page=per_page, filters=filters)
    elif current_user.role == "education_institute" and current_user.education_institute_id is not None:
        institute = repository.get_by_id(db, current_user.education_institute_id)
        if institute:
            items = [institute]
            total = 1
        else:
            items = []
            total = 0
    
    return Page(
        items=items,
        pagination=PaginationInfo(
            page=page,
            per_page=per_page,
            total=total,
            total_pages=max(1, math.ceil(total / per_page)) if total > 0 else 0,
        ),
        filters=FilterInfo(applied=list(filters.keys()), available=AVAILABLE_FILTERS),
    )

    

    