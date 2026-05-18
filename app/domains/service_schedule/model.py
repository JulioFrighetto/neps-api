from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class ServiceSchedule(Base):
    __tablename__ = "service_schedules"
    __table_args__ = (
        UniqueConstraint("service_room_id", "week_day", "shift", name="uq_service_slot"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    service_room_id: Mapped[int] = mapped_column(ForeignKey("service_rooms.id"), nullable=False)
    week_day: Mapped[str] = mapped_column(String(3), nullable=False)
    shift: Mapped[str] = mapped_column(String(3), nullable=False)
    student_id: Mapped[int | None] = mapped_column(ForeignKey("students.id"), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    service_room: Mapped["ServiceRoom"] = relationship(  # noqa: F821
        "ServiceRoom", back_populates="service_schedules"
    )
    student: Mapped["Student | None"] = relationship(  # noqa: F821
        "Student", back_populates="service_schedules"
    )
