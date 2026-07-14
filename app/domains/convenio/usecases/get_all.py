import math

from sqlalchemy.orm import Session

from app.core.schemas import FilterInfo, Page, PaginationInfo
from app.domains.convenio import repository
from app.domains.convenio.constants import AVAILABLE_FILTERS

def get_all_usecase(db: Session, page: int, per_page: int, filters: dict) -> Page:
    items, total = repository.get_all(db, page=page, per_page=per_page, filters=filters)

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
