from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Service(Base):
    __tablename__ = "services"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    region_id: Mapped[int | None] = mapped_column(ForeignKey("regions.id"), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )
    
    region: Mapped["Region | None"] = relationship("Region", back_populates="services")  # noqa: F821

    service_rooms: Mapped[list["ServiceRoom"]] = relationship(  # noqa: F821
        "ServiceRoom", back_populates="service", cascade="all, delete-orphan"
    )
    rooms: Mapped[list["Room"]] = relationship("Room", back_populates="service")  # noqa: F821
    users: Mapped[list["User"]] = relationship("User", back_populates="service")  # noqa: F821

    @property
    def user_id(self) -> int | None:
        return self.users[0].id if self.users else None

    @property
    def email(self) -> str | None:
        return self.users[0].email if self.users else None
