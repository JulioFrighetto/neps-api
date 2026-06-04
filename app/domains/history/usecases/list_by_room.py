from fastapi import HTTPException, status
from app.domains.history import repository
from app.domains.room.repository import get_by_id as get_room_by_id


def list_by_room_usecase(db, data, current_user):
    """Return (items, total) for histories filtered by room with permission checks."""
    room = get_room_by_id(db, data.id)
    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sala não encontrada")

    if current_user.role == "internships":
        if current_user.internships_id is None or current_user.internships_id != room.internships_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado")
    elif current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado")

    return repository.get_by_room(db, data.id, page=data.page, per_page=data.per_page)
