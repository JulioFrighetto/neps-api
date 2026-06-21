from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Table, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

course_disciplines = Table(
    "course_disciplines",
    Base.metadata,
    Column("course_id", ForeignKey("courses.id"), primary_key=True),
    Column("discipline_id", ForeignKey("disciplines.id"), primary_key=True),
)


class Course(Base):
    __tablename__ = "courses"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    area: Mapped[str | None] = mapped_column(String(100), nullable=True)
    workload: Mapped[int | None] = mapped_column(Integer, nullable=True)
    semester: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    disciplines: Mapped[list["Discipline"]] = relationship(
        "Discipline", secondary=course_disciplines, back_populates="courses"
    )
    education_institutes: Mapped[list["EducationInstitute"]] = relationship(  # noqa: F821
        "EducationInstitute",
        secondary="education_institute_courses",
        back_populates="courses",
    )
