from fastapi import HTTPException, status
from app.domains.history import repository
from app.domains.student.repository import get_by_id as get_student_by_id

def list_by_student_usecase(db, data, current_user):
    """Return (items, total) for histories filtered by student with permission checks."""
    student = get_student_by_id(db, data.id)
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Aluno não encontrado")

    if current_user.role == "education_institute":
        if (
            current_user.education_institute_id is None
            or current_user.education_institute_id != student.edu_institute_id
        ):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado")
    elif current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado")

    return repository.get_by_student(db, data.id, page=data.page, per_page=data.per_page)
