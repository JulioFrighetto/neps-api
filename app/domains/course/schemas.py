from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DisciplineItem(BaseModel):
    id: int | None = None
    name: str | None = None
    code: str | None = None
    region_id: int | None = None
    requires_gurney: bool = False


class CourseBase(BaseModel):
    name: str
    area: str | None = None
    workload: int | None = None
    semester: int | None = None
    is_active: bool = True


class CourseCreate(CourseBase):
    disciplines: list[DisciplineItem] = []


class CourseUpdate(BaseModel):
    name: str | None = None
    area: str | None = None
    workload: int | None = None
    semester: int | None = None
    is_active: bool | None = None
    disciplines: list[DisciplineItem] | None = None


class DisciplineBrief(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    code: str | None = None
    requires_gurney: bool = False


class CourseResponse(CourseBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime
    updated_at: datetime
    disciplines: list[DisciplineBrief] = []


class CourseFilters(BaseModel):
    name_like: str | None = None

    @classmethod
    def available_filters(cls):
        return list(cls.model_fields.keys())


class CourseGetRequest(BaseModel):
    course_id: int


class CourseBrief(BaseModel):
    id: int
    name: str


class CourseUpdateRequest(CourseUpdate):
    course_id: int
