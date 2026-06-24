from datetime import datetime
from typing import Literal

from sqlalchemy import Column, DateTime, ForeignKey, String, Table, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.domains.student.model import Student

DayOfWeek = Literal["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY", "SUNDAY"]
Period = Literal["MORNING", "AFTERNOON", "EVENING"]

schedule_period_students = Table(
    "schedule_period_students",
    Base.metadata,
    Column("schedule_period_id", ForeignKey("schedule_periods.id"), primary_key=True),
    Column("student_id", ForeignKey("students.id"), primary_key=True),
)

class Schedule(Base):
    __tablename__ = "schedules"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id"), nullable=False, unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    days: Mapped[list["ScheduleDay"]] = relationship(
        "ScheduleDay", back_populates="schedule", cascade="all, delete-orphan"
    )

class ScheduleDay(Base):
    __tablename__ = "schedule_days"
    __table_args__ = (UniqueConstraint("schedule_id", "day_of_week", name="uq_schedule_day"),)

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    schedule_id: Mapped[int] = mapped_column(ForeignKey("schedules.id"), nullable=False)
    day_of_week: Mapped[str] = mapped_column(String(20), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    schedule: Mapped["Schedule"] = relationship("Schedule", back_populates="days")
    periods: Mapped[list["SchedulePeriod"]] = relationship(
        "SchedulePeriod", back_populates="day", cascade="all, delete-orphan"
    )

class SchedulePeriod(Base):
    __tablename__ = "schedule_periods"
    __table_args__ = (UniqueConstraint("schedule_day_id", "period", name="uq_schedule_period"),)

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    schedule_day_id: Mapped[int] = mapped_column(ForeignKey("schedule_days.id"), nullable=False)
    period: Mapped[str] = mapped_column(String(20), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    day: Mapped["ScheduleDay"] = relationship("ScheduleDay", back_populates="periods")
    students: Mapped[list[Student]] = relationship(
        "Student",
        secondary=schedule_period_students,
        lazy="selectin",
    )
