from datetime import datetime

from pydantic import BaseModel
from sqlalchemy import Boolean, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.domains.course.model import course_disciplines
from app.domains.discipline.schemas import DisciplineUpdate
from app.domains.student.model import Student


class Discipline(Base):
    __tablename__ = "disciplines"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(20), nullable=False)
    code: Mapped[str | None] = mapped_column(String(20), nullable=True, index=True)
    region_id: Mapped[int | None] = mapped_column(ForeignKey("regions.id"), nullable=True)
    requires_gurney: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )
    students: Mapped[list["Student"]] = relationship(
        "Student", back_populates="discipline"
    )
    courses: Mapped[list["Course"]] = relationship(
        "Course", secondary=course_disciplines, back_populates="disciplines"
    )
    region: Mapped["Region | None"] = relationship("Region")  # noqa: F821

