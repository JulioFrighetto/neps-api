from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class History(Base):
    __tablename__ = "histories"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    period_id: Mapped[int] = mapped_column(ForeignKey("periods.id"), nullable=False, index=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"), nullable=False, index=True)
    schedule_id: Mapped[int | None] = mapped_column(ForeignKey("schedules.id"), nullable=True, index=True)
    room_id: Mapped[int | None] = mapped_column(ForeignKey("rooms.id"), nullable=True, index=True)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    period: Mapped["Period"] = relationship("Period", back_populates="histories")  # noqa: F821
    student: Mapped["Student"] = relationship("Student", back_populates="histories")  # noqa: F821
    schedule: Mapped["Schedule"] = relationship("Schedule")  # noqa: F821
    room: Mapped["Room"] = relationship("Room")  # noqa: F821
