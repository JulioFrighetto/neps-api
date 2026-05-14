from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict

StudentStatus = Literal["PENDING", "PLACED", "COMPLETED"]


class StudentBase(BaseModel):
    edu_institute_id: int
    course_id: int
    status: StudentStatus = "PENDING"
    is_active: bool = True


class StudentCreate(StudentBase):
    pass


class StudentUpdate(BaseModel):
    course_id: int | None = None
    status: StudentStatus | None = None
    is_active: bool | None = None


class StudentResponse(StudentBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
