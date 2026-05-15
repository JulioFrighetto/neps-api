from datetime import datetime

from pydantic import BaseModel, ConfigDict


class EducationInstituteBase(BaseModel):
    name: str
    is_active: bool = True


class EducationInstituteCreate(EducationInstituteBase):
    pass


class EducationInstituteUpdate(BaseModel):
    name: str | None = None
    is_active: bool | None = None


class EducationInstituteResponse(EducationInstituteBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
