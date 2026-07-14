from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.domains.convenio.constants import CONVENIO_STATUSES, STATUS_EM_ANALISE

def _validate_status(v: str | None) -> str | None:
    if v is not None and v not in CONVENIO_STATUSES:
        raise ValueError(f"status deve ser um de: {', '.join(CONVENIO_STATUSES)}")
    return v

class ConvenioBase(BaseModel):
    name: str
    description: str | None = None
    is_active: bool = True
    cnpj: str | None = None
    address: str | None = None
    phone: str | None = None
    email: str | None = None
    priority: int = Field(0, ge=0, le=1, description="0 = prioritário, 1 = não prioritário")
    status: str = STATUS_EM_ANALISE

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        return _validate_status(v)

class ConvenioCreate(ConvenioBase):
    user_name: str | None = None
    user_email: EmailStr | None = None
    region_ids: list[int] | None = None

class ConvenioUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    is_active: bool | None = None
    cnpj: str | None = None
    address: str | None = None
    phone: str | None = None
    email: str | None = None
    priority: int | None = Field(None, ge=0, le=1, description="0 = prioritário, 1 = não prioritário")
    status: str | None = None
    user_name: str | None = None
    user_email: EmailStr | None = None
    region_ids: list[int] | None = None

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str | None) -> str | None:
        return _validate_status(v)

class ConvenioResponse(ConvenioBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    education_institute_id: int | None = None
    created_at: datetime
    updated_at: datetime

class ConvenioBrief(BaseModel):
    id: int
    name: str
    status: str

class ConvenioFilters(BaseModel):
    name_like: Optional[str] = None
    cnpj: Optional[str] = None
    is_active: Optional[bool] = None
    priority: Optional[int] = None
    status: Optional[str] = None
    education_institute_id: Optional[int] = None
