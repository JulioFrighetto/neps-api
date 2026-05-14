from datetime import datetime
from typing import Literal

from sqlalchemy import Boolean, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

StudentStatus = Literal["PENDING", "PLACED", "COMPLETED"]


class Student(Base):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    edu_institute_id: Mapped[int] = mapped_column(
        ForeignKey("education_institutions.id"), nullable=False
    )
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="PENDING", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    education_institution: Mapped["EducationInstitution"] = relationship(  # noqa: F821
        "EducationInstitution", back_populates="students"
    )
    course: Mapped["Course"] = relationship("Course", back_populates="students")  # noqa: F821
    internship_records: Mapped[list["InternshipRecord"]] = relationship(  # noqa: F821
        "InternshipRecord", back_populates="student"
    )
    timetable_slots: Mapped[list["TimeTableStudent"]] = relationship(  # noqa: F821
        "TimeTableStudent", back_populates="student"
    )
