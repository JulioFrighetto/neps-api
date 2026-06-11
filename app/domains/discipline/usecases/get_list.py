import math

from app.core.schemas import FilterInfo, Page, PaginationInfo
from app.domains.discipline import repository
from app.domains.discipline.schemas import DisciplineFilters


def getList(db, page, per_page, filters):
    items, total = repository.get_all(
        db,
        page=page,
        per_page=per_page,
        filters=filters,
    )

    return Page(
        items=items,
    )
    