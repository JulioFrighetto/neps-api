from datetime import datetime

from pydantic import BaseModel, ConfigDict


class EducationInstitutionBase(BaseModel):
    name: str
    is_active: bool = True


class EducationInstitutionCreate(EducationInstitutionBase):
    pass


class EducationInstitutionUpdate(BaseModel):
    name: str | None = None
    is_active: bool | None = None


class EducationInstitutionResponse(EducationInstitutionBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
