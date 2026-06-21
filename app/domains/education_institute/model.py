from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, Integer, func
from sqlalchemy import Table, Column, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.domains.student.model import Student
from app.domains.user.model import User

education_institute_courses = Table(
    "education_institute_courses",
    Base.metadata,
    Column("education_institute_id", Integer, ForeignKey("education_institutes.id"), primary_key=True),
    Column("course_id", Integer, ForeignKey("courses.id"), primary_key=True),
)


class EducationInstitute(Base):
    __tablename__ = "education_institutes"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(20), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    cnpj: Mapped[str | None] = mapped_column(String(30), nullable=True)
    address: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    email: Mapped[str | None] = mapped_column(String(150), nullable=True)
    priority: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    students: Mapped[list["Student"]] = relationship(
        "Student", back_populates="education_institute"
    )
    users: Mapped[list["User"]] = relationship(
        "User", back_populates="education_institute"
    )
    education_institute_regions = Table(
        "education_institute_regions",
        Base.metadata,
        Column("education_institute_id", Integer, ForeignKey("education_institutes.id")),
        Column("region_id", Integer, ForeignKey("regions.id")),
    )
    regions: Mapped[list["Region"]] = relationship(
        "Region", secondary="education_institute_regions", back_populates="education_institutes"
    )
    courses: Mapped[list["Course"]] = relationship(  # noqa: F821
        "Course", secondary=education_institute_courses, back_populates="education_institutes"
    )

    @property
    def region_id(self) -> int | None:
        return self.regions[0].id if self.regions else None

    @property
    def region(self) -> "Region | None":
        return self.regions[0] if self.regions else None
