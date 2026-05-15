from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class EducationInstitute(Base):
    __tablename__ = "education_institutes"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(20), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    courses: Mapped[list["Course"]] = relationship(  # noqa: F821
        "Course", back_populates="education_institute"
    )
    students: Mapped[list["Student"]] = relationship(  # noqa: F821
        "Student", back_populates="education_institute"
    )
    # users relationship will be added when the User domain is implemented
