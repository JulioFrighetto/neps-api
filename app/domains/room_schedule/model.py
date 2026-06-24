from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

class RoomSchedule(Base):
    __tablename__ = "room_schedules"
    __table_args__ = (
        UniqueConstraint("room_id", "week_day", "shift", name="uq_room_slot"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id"), nullable=False)
    week_day: Mapped[str] = mapped_column(String(3), nullable=False)
    shift: Mapped[str] = mapped_column(String(5), nullable=False)
    capacity: Mapped[int] = mapped_column(Integer, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    students: Mapped[list["RoomScheduleStudent"]] = relationship(
        "RoomScheduleStudent", back_populates="schedule"
    )

class RoomScheduleStudent(Base):
    __tablename__ = "room_schedule_students"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    room_schedule_id: Mapped[int] = mapped_column(ForeignKey("room_schedules.id"), nullable=False)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    schedule: Mapped["RoomSchedule"] = relationship("RoomSchedule", back_populates="students")
