from datetime import datetime

from pydantic import BaseModel, ConfigDict


class HealthCenterBase(BaseModel):
    name: str
    region_id: int | None = None
    is_active: bool = True


class HealthCenterCreate(HealthCenterBase):
    pass


class HealthCenterUpdate(BaseModel):
    name: str | None = None
    region_id: int | None = None
    is_active: bool | None = None


class HealthCenterResponse(HealthCenterBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


# Region schemas
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
