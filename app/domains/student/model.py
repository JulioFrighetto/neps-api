from datetime import datetime
from typing import Literal

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

StudentStatus = Literal["PENDING", "PLACED", "COMPLETED"]


class Student(Base):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    edu_institute_id: Mapped[int] = mapped_column(
        ForeignKey("education_institutes.id"), nullable=False
    )
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id"), nullable=False)
    name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    cpf: Mapped[str | None] = mapped_column(String(20), nullable=True)
    email: Mapped[str | None] = mapped_column(String(150), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    semester: Mapped[int | None] = mapped_column(Integer, nullable=True)
    document_url: Mapped[str] = mapped_column(String(500), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="PENDING", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    education_institute: Mapped["EducationInstitute"] = relationship(  # noqa: F821
        "EducationInstitute", back_populates="students"
    )
    course: Mapped["Course"] = relationship("Course", back_populates="students")  # noqa: F821
    service_schedules: Mapped[list["ServiceSchedule"]] = relationship(  # noqa: F821
        "ServiceSchedule", back_populates="student"
    )

    periods: Mapped[list["Period"]] = relationship(
        "Period",
        secondary="period_students",
        back_populates="students",
    )
