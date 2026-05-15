from datetime import datetime

from pydantic import BaseModel, ConfigDict


class RegionCreate(BaseModel):
    name: str
    priority_education_institute: int | None = None
    is_active: bool = True
    pass


class RegionUpdate(BaseModel):
    name: str | None = None
    priority_education_institute: int | None = None
    is_active: bool | None = None


class RegionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    priority_education_institute: int | None = None
    is_active: bool = True
