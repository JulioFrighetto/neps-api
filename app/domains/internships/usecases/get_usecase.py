from fastapi import HTTPException, status
from app.domains.internships import repository

def get_internship_usecase(db, internships_id: int):
    """Retrieve an internship by id, raising 404 if not found."""
    internship = repository.get_by_id(db, internships_id)
    if not internship:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campo de estágio não encontrado")
    return internship
