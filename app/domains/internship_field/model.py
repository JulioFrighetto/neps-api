from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class InternshipField(Base):
    __tablename__ = "internship_field"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    region_id: Mapped[int | None] = mapped_column(ForeignKey("regions.id"), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    rooms: Mapped[list["Room"]] = relationship("Room", back_populates="internship_field")  # noqa: F821
    # users relationship will be added when the User domain is implemented


class Region(Base):
    __tablename__ = "regions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    priority_education_institution: Mapped[int | None] = mapped_column(
        ForeignKey("education_institutions.id"), nullable=True
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    internship_field: Mapped[list["InternshipField"]] = relationship(
        "InternshipField", foreign_keys="InternshipField.region_id"
    )
