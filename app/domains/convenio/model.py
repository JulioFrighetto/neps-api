from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.domains.convenio.constants import STATUS_EM_ANALISE

if TYPE_CHECKING:
    from app.domains.education_institute.model import EducationInstitute

class Convenio(Base):
    __tablename__ = "convenios"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    cnpj: Mapped[str | None] = mapped_column(String(30), nullable=True)
    address: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    email: Mapped[str | None] = mapped_column(String(150), nullable=True)
    priority: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default=STATUS_EM_ANALISE, nullable=False)
    education_institute_id: Mapped[int | None] = mapped_column(
        ForeignKey("education_institutes.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    education_institute: Mapped["EducationInstitute | None"] = relationship("EducationInstitute")
