from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CourseBase(BaseModel):
    edu_institution_id: int
    name: str
    requires_gurney: bool = False


class CourseCreate(CourseBase):
    pass


class CourseUpdate(BaseModel):
    name: str | None = None
    requires_gurney: bool | None = None


class CourseResponse(CourseBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
