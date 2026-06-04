from fastapi import HTTPException, status
from app.domains.internships import repository
from app.core.schemas import FilterInfo, PaginationInfo
import math

def list_internships_usecase(db, page, per_page, filters, current_user):
    """Return (items, total) applying role‑based access rules."""
    if current_user.role == "admin":
        items, total = repository.get_all(db, page=page, per_page=per_page, filters=filters)
    elif current_user.role == "internships" and current_user.internships_id is not None:
        internship = repository.get_by_id(db, current_user.internships_id)
        items = [internship] if internship else []
        total = 1 if internship else 0
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado")
    return items, total
