from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict

InternshipStatus = Literal["ACTIVE", "RENEWED", "CANCELED", "ENDED"]
InternshipSlotStatus = Literal["OPEN", "FILLED", "CLOSED"]


# ── Internship (slot) ─────────────────────────────────────────────────────────

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


# ── InternshipRecord ──────────────────────────────────────────────────────────

class InternshipRecordBase(BaseModel):
    internship_id: int
    student_id: int
    contract_start_date: datetime
    contract_end_date: datetime
    end_date: datetime | None = None
    status: InternshipStatus = "ACTIVE"


class InternshipRecordCreate(InternshipRecordBase):
    pass


class InternshipRecordUpdate(BaseModel):
    end_date: datetime | None = None
    status: InternshipStatus | None = None


class InternshipRecordResponse(InternshipRecordBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


# ── InternshipDocument ────────────────────────────────────────────────────────

class InternshipDocumentBase(BaseModel):
    internship_id: int
    record_id: int | None = None
    url: str


class InternshipDocumentCreate(InternshipDocumentBase):
    pass


class InternshipDocumentResponse(InternshipDocumentBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
