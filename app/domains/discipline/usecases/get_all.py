import math
from app.core.schemas import FilterInfo, Page, PaginationInfo
from app.domains.discipline import repository
from app.domains.discipline.schemas import DisciplineFilters


def get_all_usecase(db, page, per_page, filters):
    items, total = repository.get_all(
        db,
        page=page,
        per_page=per_page,
        filters=filters,
    )

    return Page(
        items=items,
        pagination=PaginationInfo(
            page=page,
            per_page=per_page,
            total=total,
            total_pages=max(1, math.ceil(total / per_page))
            if total > 0 else 0,
        ),
        filters=FilterInfo(
            applied=list(filters.keys()),
            available=DisciplineFilters.available_filters(),
        ),
    )
    