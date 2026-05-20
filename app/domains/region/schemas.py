from datetime import datetime

from pydantic import BaseModel, ConfigDict


class RegionCreate(BaseModel):
    name: str
    is_active: bool = True


class RegionUpdate(BaseModel):
    name: str | None = None
    is_active: bool | None = None


class RegionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    is_active: bool
