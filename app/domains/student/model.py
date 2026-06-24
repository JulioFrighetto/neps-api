from datetime import datetime, date
from typing import Literal

from sqlalchemy import Boolean, DateTime, Date, ForeignKey, Integer, String, func, LargeBinary
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.domains.education_institute.model import EducationInstitute
if TYPE_CHECKING:
    from app.domains.discipline.model import Discipline
if TYPE_CHECKING:
    from app.domains.internships.model import Internship
from app.domains.internships_schedule.model import InternshipsSchedule
from app.domains.period.model import Period
from app.domains.history.model import History

StudentStatus = Literal["PENDING", "PLACED", "COMPLETED"]

class Student(Base):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    edu_institute_id: Mapped[int] = mapped_column(
        ForeignKey("education_institutes.id"), nullable=False
    )
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id"), nullable=False)
    discipline_id: Mapped[int] = mapped_column(ForeignKey("disciplines.id"), nullable=False)
    name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    cpf: Mapped[str | None] = mapped_column(String(20), nullable=True)
    email: Mapped[str | None] = mapped_column(String(150), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    semester: Mapped[int | None] = mapped_column(Integer, nullable=True)
    document_url: Mapped[str] = mapped_column(String(500), nullable=False)
    director_signed_pdf: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)
    internship_start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    internship_expected_end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    internship_id: Mapped[int | None] = mapped_column(ForeignKey("internships.id"), nullable=True)
    professor_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    preceptor_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="PENDING", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    education_institute: Mapped["EducationInstitute"] = relationship(
        "EducationInstitute", back_populates="students"
    )
    discipline: Mapped["Discipline"] = relationship("Discipline", back_populates="students")
    internship: Mapped["Internship | None"] = relationship(
        "Internship", back_populates="students"
    )
    internships_schedules: Mapped[list["InternshipsSchedule"]] = relationship(
        "InternshipsSchedule", back_populates="student"
    )

    periods: Mapped[list["Period"]] = relationship(
        "Period",
        secondary="period_students",
        back_populates="students",
    )
    histories: Mapped[list["History"]] = relationship("History", back_populates="student")
