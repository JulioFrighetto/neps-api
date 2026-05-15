from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Room(Base):
    __tablename__ = "rooms"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    internship_field_id: Mapped[int] = mapped_column(ForeignKey("internship_fields.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(20), nullable=False)
    room_capacity: Mapped[int] = mapped_column(Integer, nullable=False)
    has_gurney: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    internship_field: Mapped["InternshipField"] = relationship(  # noqa: F821
        "InternshipField", back_populates="rooms"
    )
    internships: Mapped[list["Internship"]] = relationship(  # noqa: F821
        "Internship", back_populates="room"
    )
    schedules: Mapped[list["RoomSchedule"]] = relationship(
        "RoomSchedule", back_populates="room"
    )


class RoomSchedule(Base):
    __tablename__ = "room_schedules"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id"), nullable=False)
    week_day: Mapped[str] = mapped_column(String(3), nullable=False)  # SEG, TER, QUA, QUI, SEX

    # Relationships
    room: Mapped["Room"] = relationship("Room", back_populates="schedules")
    timetables: Mapped[list["RoomTimeTable"]] = relationship(
        "RoomTimeTable", back_populates="schedule"
    )


class RoomTimeTable(Base):
    __tablename__ = "room_timetables"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    schedule_id: Mapped[int] = mapped_column(ForeignKey("room_schedules.id"), nullable=False)
    time_table: Mapped[str] = mapped_column(String(3), nullable=False)  # MAN, TRD, VSP
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    schedule: Mapped["RoomSchedule"] = relationship("RoomSchedule", back_populates="timetables")
    student_slot: Mapped["TimeTableStudent"] = relationship(
        "TimeTableStudent", back_populates="timetable", uselist=False
    )


class TimeTableStudent(Base):
    __tablename__ = "timetable_students"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    timetable_id: Mapped[int] = mapped_column(ForeignKey("room_timetables.id"), nullable=False)
    student_id: Mapped[int | None] = mapped_column(
        ForeignKey("students.id"), nullable=True
    )  # NULL = slot is vacant

    # Relationships
    timetable: Mapped["RoomTimeTable"] = relationship(
        "RoomTimeTable", back_populates="student_slot"
    )
    student: Mapped["Student"] = relationship(  # noqa: F821
        "Student", back_populates="timetable_slots"
    )
