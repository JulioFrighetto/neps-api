from datetime import datetime
from typing import Literal

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

InternshipStatus = Literal["ACTIVE", "RENEWED", "CANCELED", "ENDED"]
InternshipSlotStatus = Literal["OPEN", "FILLED", "CLOSED"]


class Internship(Base):

    __tablename__ = "internships"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id"), nullable=False)
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id"), nullable=False)
    student_id: Mapped[int | None] = mapped_column(ForeignKey("students.id"), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="OPEN", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    course: Mapped["Course"] = relationship("Course", back_populates="internships")  # noqa: F821
    room: Mapped["Room"] = relationship("Room", back_populates="internships")  # noqa: F821
    student: Mapped["Student | None"] = relationship(  # noqa: F821
        "Student", foreign_keys=[student_id]
    )
