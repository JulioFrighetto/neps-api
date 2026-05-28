from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

StudentStatus = Literal["PENDING", "PLACED", "COMPLETED"]


class StudentBase(BaseModel):
    edu_institute_id: int
    course_id: int
    status: StudentStatus = "PENDING"
    is_active: bool = True


class StudentCreate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    
    edu_institute_id: int = Field(validation_alias="institution_id")
    course_id: int
    status: StudentStatus = "PENDING"
    is_active: bool = True
    name: str | None = None
    cpf: str | None = None
    email: str | None = None
    phone: str | None = None
    semester: int | None = None
    document_url: str = Field(min_length=1, description="URL do documento PDF no Cloudinary (máximo 5MB)")


class StudentUpdate(BaseModel):
    course_id: int | None = None
    status: StudentStatus | None = None
    is_active: bool | None = None


class StudentResponse(StudentBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime

    document_url: str
