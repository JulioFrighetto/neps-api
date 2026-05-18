from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(150), nullable=False, unique=True, index=True)
    password: Mapped[str] = mapped_column(String(255), nullable=True)
    role: Mapped[str] = mapped_column(String(20), nullable=False, default="user")
    service_id: Mapped[int | None] = mapped_column(ForeignKey("services.id"), nullable=True, unique=True)
    education_institute_id: Mapped[int | None] = mapped_column(
        ForeignKey("education_institutes.id"), nullable=True
    )
    internship_field_id: Mapped[int | None] = mapped_column(
        ForeignKey("internship_field.id"), nullable=True
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    service = relationship("Service", back_populates="user")
    education_institute = relationship("EducationInstitute", back_populates="users")
    internship_field = relationship("InternshipField", back_populates="users")