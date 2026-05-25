from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CourseBase(BaseModel):
    name: str
    requires_gurney: bool = False
    code: str | None = None
    region_id: int | None = None


class CourseCreate(CourseBase):
    pass


class CourseUpdate(BaseModel):
    name: str | None = None
    requires_gurney: bool | None = None
    code: str | None = None
    region_id: int | None = None


class CourseResponse(CourseBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
