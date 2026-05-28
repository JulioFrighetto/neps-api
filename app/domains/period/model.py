from datetime import datetime

from sqlalchemy import Boolean, Date, DateTime, String, func, Table, Column, Integer, ForeignKey, Date as SQLDate
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


period_students = Table(
    "period_students",
    Base.metadata,
    Column("period_id", Integer, ForeignKey("periods.id")),
    Column("student_id", Integer, ForeignKey("students.id")),
)


class Period(Base):
    __tablename__ = "periods"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    priority_start_date: Mapped[datetime] = mapped_column(SQLDate, nullable=False)
    priority_end_date: Mapped[datetime] = mapped_column(SQLDate, nullable=False)
    start_date: Mapped[datetime] = mapped_column(SQLDate, nullable=False)
    end_date: Mapped[datetime] = mapped_column(SQLDate, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    students: Mapped[list["Student"]] = relationship(
        "Student", secondary=period_students, back_populates="periods"
    )