from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.domains.internships_room.model import InternshipsRoom
if TYPE_CHECKING:
    from app.domains.student.model import Student

class InternshipsSchedule(Base):
    __tablename__ = "internships_schedules"
    __table_args__ = (
        UniqueConstraint("internships_room_id", "week_day", "shift", name="uq_internships_slot"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    internships_room_id: Mapped[int] = mapped_column(ForeignKey("internships_rooms.id"), nullable=False)
    week_day: Mapped[str] = mapped_column(String(3), nullable=False)
    shift: Mapped[str] = mapped_column(String(3), nullable=False)
    student_id: Mapped[int | None] = mapped_column(ForeignKey("students.id"), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    internships_room: Mapped["InternshipsRoom"] = relationship(
        "InternshipsRoom", back_populates="internships_schedules"
    )
    student: Mapped["Student | None"] = relationship(
        "Student", back_populates="internships_schedules"
    )
