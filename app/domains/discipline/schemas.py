from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DisciplineBase(BaseModel):
    name: str
    requires_gurney: bool = False
    code: str | None = None
    region_id: int | None = None

class DisciplineCreate(DisciplineBase):
    pass

class DisciplineUpdate(BaseModel):
    name: str | None = None
    requires_gurney: bool | None = None
    code: str | None = None
    region_id: int | None = None

class DisciplineResponse(DisciplineBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime
    updated_at: datetime

class DisciplineFilters(BaseModel):
    name_like: str | None = None
    code_like: str | None = None
    region_id: int | None = None

    @classmethod
    def available_filters(cls):
        return list(cls.model_fields.keys())

class DisciplineGetRequest(BaseModel):
    discipline_id: int

class DisciplineUpdateRequest(DisciplineUpdate):
    discipline_id: int