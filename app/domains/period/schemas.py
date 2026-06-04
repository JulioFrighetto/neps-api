from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class PeriodBase(BaseModel):
    name: str
    priority_start_date: date
    priority_end_date: date
    start_date: date
    end_date: date
    is_active: bool = True


class PeriodCreate(PeriodBase):
    pass


class PeriodUpdate(BaseModel):
    name: str | None = None
    priority_start_date: date | None = None
    priority_end_date: date | None = None
    start_date: date | None = None
    end_date: date | None = None
    is_active: bool | None = None


class PeriodResponse(PeriodBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class StudentSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str | None
    cpf: str | None
    semester: int | None = None
    has_slot: bool = False
    
    class Discipline(BaseModel):
        model_config = ConfigDict(from_attributes=True)
        id: int
        name: str

    class Institution(BaseModel):
        model_config = ConfigDict(from_attributes=True)
        id: int
        name: str
    
    class Slot(BaseModel):
        model_config = ConfigDict(from_attributes=True)
        room_id: int
        room_name: str | None = None
        day_of_week: str
        period: str

    discipline: Discipline | None = None
    institution: Institution | None = None
    slot: Slot | None = None


class PeriodDetailResponse(PeriodResponse):
    students: list[StudentSummary] = []
    student_ids: list[int] = []


class StudentLinkRequest(BaseModel):
    student_id: int