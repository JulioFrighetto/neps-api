from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.domains.internships.model import Internship


class Room(Base):
    __tablename__ = "rooms"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    internship_id: Mapped[int] = mapped_column(ForeignKey("internships.id"), nullable=False, name="internships_id")
    name: Mapped[str] = mapped_column(String(20), nullable=False)
    room_capacity: Mapped[int] = mapped_column(Integer, nullable=False)
    has_gurney: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    internships: Mapped["Internship"] = relationship("Internship", back_populates="rooms")  # noqa: F821