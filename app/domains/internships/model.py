from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.domains.region.model import Region
from app.domains.internships_room.model import InternshipsRoom
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.domains.room.model import Room
if TYPE_CHECKING:
    from app.domains.student.model import Student
from app.domains.user.model import User

class Internship(Base):
    __tablename__ = "internships"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    region_id: Mapped[int | None] = mapped_column(ForeignKey("regions.id"), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    region: Mapped["Region | None"] = relationship("Region", back_populates="internships")

    internships_rooms: Mapped[list["InternshipsRoom"]] = relationship(
        "InternshipsRoom", back_populates="internships", cascade="all, delete-orphan"
    )
    rooms: Mapped[list["Room"]] = relationship("Room", back_populates="internships")
    students: Mapped[list["Student"]] = relationship("Student", back_populates="internship")
    users: Mapped[list["User"]] = relationship("User", back_populates="internships")

    @property
    def user_id(self) -> int | None:
        return self.users[0].id if self.users else None

    @property
    def email(self) -> str | None:
        return self.users[0].email if self.users else None
