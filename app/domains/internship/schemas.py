from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict

InternshipStatus = Literal["ACTIVE", "RENEWED", "CANCELED", "ENDED"]
InternshipSlotStatus = Literal["OPEN", "FILLED", "CLOSED"]


class InternshipBase(BaseModel):
    course_id: int
    room_id: int
    student_id: int | None = None
    status: InternshipSlotStatus = "OPEN"
    is_active: bool = True


class InternshipCreate(InternshipBase):
    pass


class InternshipUpdate(BaseModel):
    student_id: int | None = None
    status: InternshipSlotStatus | None = None
    is_active: bool | None = None


class InternshipResponse(InternshipBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
