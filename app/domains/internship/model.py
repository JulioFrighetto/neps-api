from datetime import datetime
from typing import Literal

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

InternshipStatus = Literal["ACTIVE", "RENEWED", "CANCELED", "ENDED"]
InternshipSlotStatus = Literal["OPEN", "FILLED", "CLOSED"]


class Internship(Base):
    """Active internship slot — links a student to a room via a course."""

    __tablename__ = "internships"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id"), nullable=False)
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id"), nullable=False)
    student_id: Mapped[int | None] = mapped_column(ForeignKey("students.id"), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="OPEN", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    course: Mapped["Course"] = relationship("Course", back_populates="internships")  # noqa: F821
    room: Mapped["Room"] = relationship("Room", back_populates="internships")  # noqa: F821
    student: Mapped["Student | None"] = relationship(  # noqa: F821
        "Student", foreign_keys=[student_id]
    )
    records: Mapped[list["InternshipRecord"]] = relationship(
        "InternshipRecord", back_populates="internship"
    )
    documents: Mapped[list["InternshipDocument"]] = relationship(
        "InternshipDocument", back_populates="internship"
    )


class InternshipRecord(Base):
    """Historical log of a student's internship contract lifecycle."""

    __tablename__ = "internship_records"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    internship_id: Mapped[int] = mapped_column(ForeignKey("internships.id"), nullable=False)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"), nullable=False)
    contract_start_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    contract_end_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    end_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="ACTIVE", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    internship: Mapped["Internship"] = relationship("Internship", back_populates="records")
    student: Mapped["Student"] = relationship("Student", back_populates="internship_records")  # noqa: F821
    documents: Mapped[list["InternshipDocument"]] = relationship(
        "InternshipDocument", back_populates="record"
    )


class InternshipDocument(Base):
    """Stores paths to signed contract documents in external storage."""

    __tablename__ = "internship_documents"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    internship_id: Mapped[int] = mapped_column(ForeignKey("internships.id"), nullable=False)
    record_id: Mapped[int | None] = mapped_column(
        ForeignKey("internship_records.id"), nullable=True
    )
    url: Mapped[str] = mapped_column(Text, nullable=False)

    # Relationships
    internship: Mapped["Internship"] = relationship("Internship", back_populates="documents")
    record: Mapped["InternshipRecord | None"] = relationship(
        "InternshipRecord", back_populates="documents"
    )
