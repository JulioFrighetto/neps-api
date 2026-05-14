from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.domains.internship import repository
from app.domains.internship.schemas import (
    InternshipCreate,
    InternshipDocumentCreate,
    InternshipDocumentResponse,
    InternshipRecordCreate,
    InternshipRecordResponse,
    InternshipRecordUpdate,
    InternshipResponse,
    InternshipUpdate,
)

router = APIRouter(tags=["Internships"])


# ── Internship slots ──────────────────────────────────────────────────────────

@router.get("/internships", response_model=list[InternshipResponse])
def list_internships(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return repository.get_all(db, skip=skip, limit=limit)


@router.get("/internships/{internship_id}", response_model=InternshipResponse)
def get_internship(internship_id: int, db: Session = Depends(get_db)):
    internship = repository.get_by_id(db, internship_id)
    if not internship:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Estágio não encontrado")
    return internship


@router.get("/internships/by-student/{student_id}", response_model=list[InternshipResponse])
def list_internships_by_student(student_id: int, db: Session = Depends(get_db)):
    return repository.get_by_student(db, student_id)


@router.get("/internships/by-room/{room_id}", response_model=list[InternshipResponse])
def list_internships_by_room(room_id: int, db: Session = Depends(get_db)):
    return repository.get_by_room(db, room_id)


@router.post("/internships", response_model=InternshipResponse, status_code=status.HTTP_201_CREATED)
def create_internship(data: InternshipCreate, db: Session = Depends(get_db)):
    return repository.create(db, data)


@router.patch("/internships/{internship_id}", response_model=InternshipResponse)
def update_internship(internship_id: int, data: InternshipUpdate, db: Session = Depends(get_db)):
    internship = repository.update(db, internship_id, data)
    if not internship:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Estágio não encontrado")
    return internship


@router.delete("/internships/{internship_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_internship(internship_id: int, db: Session = Depends(get_db)):
    deleted = repository.delete(db, internship_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Estágio não encontrado")


# ── Records ───────────────────────────────────────────────────────────────────

@router.get(
    "/internships/{internship_id}/records", response_model=list[InternshipRecordResponse]
)
def list_records(internship_id: int, db: Session = Depends(get_db)):
    return repository.get_records_by_internship(db, internship_id)


@router.post(
    "/internship-records",
    response_model=InternshipRecordResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_record(data: InternshipRecordCreate, db: Session = Depends(get_db)):
    return repository.create_record(db, data)


@router.patch("/internship-records/{record_id}", response_model=InternshipRecordResponse)
def update_record(record_id: int, data: InternshipRecordUpdate, db: Session = Depends(get_db)):
    record = repository.update_record(db, record_id, data)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Registro não encontrado"
        )
    return record


# ── Documents ─────────────────────────────────────────────────────────────────

@router.get(
    "/internships/{internship_id}/documents", response_model=list[InternshipDocumentResponse]
)
def list_documents(internship_id: int, db: Session = Depends(get_db)):
    return repository.get_documents_by_internship(db, internship_id)


@router.post(
    "/internship-documents",
    response_model=InternshipDocumentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_document(data: InternshipDocumentCreate, db: Session = Depends(get_db)):
    return repository.create_document(db, data)


@router.delete("/internship-documents/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(document_id: int, db: Session = Depends(get_db)):
    deleted = repository.delete_document(db, document_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Documento não encontrado"
        )
