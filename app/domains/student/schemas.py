from datetime import datetime, date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

StudentStatus = Literal["PENDING", "PLACED", "COMPLETED"]

class StudentBase(BaseModel):
    edu_institute_id: int
    course_id: int
    discipline_id: int
    status: StudentStatus = "PENDING"
    is_active: bool = True

class StudentCreate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    edu_institute_id: int = Field(validation_alias="institution_id")
    course_id: int
    discipline_id: int
    status: StudentStatus = "PENDING"
    is_active: bool = True
    name: str | None = None
    cpf: str | None = None
    email: str | None = None
    phone: str | None = None
    semester: int | None = None
    document_url: str = Field(min_length=1, description="URL do documento PDF no Cloudinary (máximo 5MB)")
    director_signed_pdf: str | None = Field(
        default=None,
        description="PDF assinado pelo diretor (base64). Opcional."
    )
    internship_start_date: date | None = Field(
        default=None,
        description="Data de início do estágio (YYYY-MM-DD). Opcional.",
    )
    internship_expected_end_date: date | None = Field(
        default=None,
        description="Data prevista para término do estágio (YYYY-MM-DD). Opcional.",
    )
    professor_name: str | None = Field(
        default=None,
        description="Nome do professor responsável. Opcional.",
    )
    preceptor_name: str | None = Field(
        default=None,
        description="Nome do preceptor. Opcional.",
    )

class StudentUpdate(BaseModel):
    course_id: int | None = None
    discipline_id: int | None = None
    status: StudentStatus | None = None
    is_active: bool | None = None
    director_signed_pdf: str | None = None
    internship_id: int | None = None
    internship_start_date: date | None = None
    internship_expected_end_date: date | None = None
    professor_name: str | None = None
    preceptor_name: str | None = None

class StudentResponse(StudentBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    course_id: int | None = None
    created_at: datetime
    updated_at: datetime

    document_url: str
    director_signed_pdf: str | None = None
    internship_id: int | None = None
    internship_start_date: date | None = None
    internship_expected_end_date: date | None = None
    professor_name: str | None = None
    preceptor_name: str | None = None
