from fastapi import HTTPException, status
from app.domains.history import repository
from app.domains.period import repository as period_repository

def list_by_period_usecase(db, data, current_user):
    """Return (items, total) for histories filtered by period.
    Performs the same permission checks as the original router.
    """
    institute_priority = None
    if current_user.role == "education_institute":
        if current_user.education_institute_id is None or current_user.education_institute is None:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado")
        institute_priority = current_user.education_institute.priority
    elif current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado")

    period = period_repository.get_by_id(db, data.id, institute_priority=institute_priority)
    if not period:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Período não encontrado")

    return repository.get_by_period(db, data.id, page=data.page, per_page=data.per_page)
