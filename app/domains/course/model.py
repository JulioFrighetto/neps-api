from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Course(Base):
    __tablename__ = "courses"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    edu_institution_id: Mapped[int] = mapped_column(
        ForeignKey("education_institutions.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(20), nullable=False)
    requires_gurney: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    education_institution: Mapped["EducationInstitution"] = relationship(  # noqa: F821
        "EducationInstitution", back_populates="courses"
    )
    students: Mapped[list["Student"]] = relationship(  # noqa: F821
        "Student", back_populates="course"
    )
    internships: Mapped[list["Internship"]] = relationship(  # noqa: F821
        "Internship", back_populates="course"
    )
