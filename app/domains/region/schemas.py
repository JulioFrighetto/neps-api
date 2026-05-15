from datetime import datetime

from pydantic import BaseModel, ConfigDict


class RegionBase(BaseModel):
    priority_education_institution: int | None = None
    is_active: bool = True


class RegionCreate(RegionBase):
    pass


class RegionUpdate(BaseModel):
    priority_education_institution: int | None = None
    is_active: bool | None = None


class RegionResponse(RegionBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
