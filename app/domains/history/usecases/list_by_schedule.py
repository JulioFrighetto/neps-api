from fastapi import HTTPException, status
from app.domains.history import repository
from app.domains.room_schedule.repository_nested import get_by_id as get_schedule_by_id
from app.domains.room.repository import get_by_id as get_room_by_id

def list_by_schedule_usecase(db, data, current_user):
    """Return (items, total) for histories filtered by schedule with permission checks."""
    schedule = get_schedule_by_id(db, data.id)
    if not schedule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Schedule não encontrado")

    room = get_room_by_id(db, schedule.room_id)
    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sala não encontrada")

    if current_user.role == "internships":
        if current_user.internship_id is None or current_user.internship_id != room.internship_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado")
    elif current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado")

    return repository.get_by_schedule(db, data.id, page=data.page, per_page=data.per_page)
