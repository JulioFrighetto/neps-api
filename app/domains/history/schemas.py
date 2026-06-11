from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class HistoryInternshipSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class HistoryStudentSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str | None = None
    cpf: str | None = None
    internship: HistoryInternshipSummary | None = None


class HistoryPeriodSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    start_date: date
    end_date: date


class HistoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    period_id: int
    student_id: int
    schedule_id: int | None = None
    room_id: int | None = None
    start_date: date
    end_date: date | None = None
    created_at: datetime
    updated_at: datetime
    student: HistoryStudentSummary | None = None
    period: HistoryPeriodSummary | None = None
