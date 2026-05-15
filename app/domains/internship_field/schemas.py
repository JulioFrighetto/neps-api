from datetime import datetime

from pydantic import BaseModel, ConfigDict


class InternshipFieldBase(BaseModel):
    name: str
    region_id: int | None = None
    is_active: bool = True


class InternshipFieldCreate(InternshipFieldBase):
    pass


class InternshipFieldUpdate(BaseModel):
    name: str | None = None
    region_id: int | None = None
    is_active: bool | None = None


class InternshipFieldResponse(InternshipFieldBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
