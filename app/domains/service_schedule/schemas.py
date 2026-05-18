from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict

WeekDay = Literal["SEG", "TER", "QUA", "QUI", "SEX", "SAB", "DOM"]
Shift = Literal["MAN", "TRD", "VSP"]


class ServiceScheduleBase(BaseModel):
    service_room_id: int
    week_day: WeekDay
    shift: Shift
    student_id: int | None = None
    is_active: bool = True


class ServiceScheduleCreate(ServiceScheduleBase):
    pass


class ServiceScheduleUpdate(BaseModel):
    week_day: WeekDay | None = None
    shift: Shift | None = None
    student_id: int | None = None
    is_active: bool | None = None


class ServiceScheduleResponse(ServiceScheduleBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
