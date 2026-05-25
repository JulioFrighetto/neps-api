from datetime import datetime

from pydantic import BaseModel, ConfigDict


class SchedulePeriodResponse(BaseModel):
    """Um período em um dia (MORNING/AFTERNOON/EVENING)."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    period: str  # MORNING, AFTERNOON, EVENING
    student_id: int | None = None
    created_at: datetime
    updated_at: datetime


class ScheduleDayResponse(BaseModel):
    """Um dia da semana com seus períodos."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    day_of_week: str  # MONDAY, TUESDAY, etc.
    periods: list[SchedulePeriodResponse] = []
    created_at: datetime
    updated_at: datetime


class ScheduleResponse(BaseModel):
    """Agenda completa de uma sala."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    room_id: int
    days: list[ScheduleDayResponse] = []
    created_at: datetime
    updated_at: datetime


# Format para retorno simplificado
class SimplifiedScheduleResponse(BaseModel):
    """Agenda simplificada com formato nested como solicitado."""
    roomId: int
    days: list[dict]
