from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class EducationInstituteBase(BaseModel):
    name: str
    is_active: bool = True
    cnpj: str | None = None
    address: str | None = None
    phone: str | None = None
    email: str | None = None
    priority: int = Field(0, ge=0, le=1, description="0 = prioritário, 1 = não prioritário")


class EducationInstituteCreate(EducationInstituteBase):
    user_name: str | None = None
    user_email: EmailStr | None = None
    region_ids: list[int] | None = None


class EducationInstituteUpdate(BaseModel):
    name: str | None = None
    is_active: bool | None = None
    cnpj: str | None = None
    address: str | None = None
    phone: str | None = None
    email: str | None = None
    priority: int | None = Field(None, ge=0, le=1, description="0 = prioritário, 1 = não prioritário")
    region_ids: list[int] | None = None


class EducationInstituteResponse(EducationInstituteBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime

    class StudentSummary(BaseModel):
        model_config = ConfigDict(from_attributes=True)
        id: int
        discipline_id: int | None = None
        status: str

    class UserSummary(BaseModel):
        model_config = ConfigDict(from_attributes=True)
        id: int
        name: str
        email: str
        role: str
        is_active: bool

    students: list[StudentSummary] = []
    users: list[UserSummary] = []

    class RegionSummary(BaseModel):
        model_config = ConfigDict(from_attributes=True)
        id: int
        name: str

    regions: list[RegionSummary] = []
    region_id: int | None = None
    region: RegionSummary | None = None

class EducationInstituteBrief(BaseModel):
    id: int
    name: str

class EducationInstituteFilters(BaseModel):
    name_like: Optional[str] = None
    cnpj: Optional[str] = None
    is_active: Optional[bool] = None
    priority: Optional[int] = None




