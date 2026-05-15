from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Room(Base):
    __tablename__ = "rooms"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    internship_field_id: Mapped[int] = mapped_column(ForeignKey("internship_field.id"), nullable=False)
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

    internships: Mapped[list["Internship"]] = relationship(
        "Internship", back_populates="room"
    )