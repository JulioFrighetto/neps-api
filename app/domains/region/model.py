from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.domains.education_institute.model import EducationInstitute
    from app.domains.internships.model import Internship


class Region(Base):
    __tablename__ = "regions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    # Backref to education institutes (many-to-many)
    education_institutes: Mapped[list["EducationInstitute"]] = relationship(
        "EducationInstitute", secondary="education_institute_regions", back_populates="regions"
    )
    internships: Mapped[list["Internship"]] = relationship(
        "Internship", back_populates="region"
    )
