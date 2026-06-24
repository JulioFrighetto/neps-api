from datetime import datetime

from pydantic import BaseModel, ConfigDict

class RoomScheduleBase(BaseModel):
    room_id: int
    week_day: str
    shift: str
    capacity: int
    is_active: bool = True

class RoomScheduleCreate(RoomScheduleBase):
    pass

class RoomScheduleUpdate(BaseModel):
    week_day: str | None = None
    shift: str | None = None
    capacity: int | None = None
    is_active: bool | None = None

class RoomScheduleResponse(RoomScheduleBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime

class RoomScheduleQuery(BaseModel):
    room_id: int
    day_of_week: str
    period: str
    period_id: int
    student_id: int
