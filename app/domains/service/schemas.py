from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class ServiceBase(BaseModel):
    name: str
    region_id: int | None = None
    is_active: bool = True


class ServiceCreate(ServiceBase):
    user_name: str | None = None
    user_email: EmailStr | None = None


class ServiceUpdate(BaseModel):
    name: str | None = None
    region_id: int | None = None
    is_active: bool | None = None
    user_name: str | None = None
    user_email: EmailStr | None = None


class ServiceUserSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: EmailStr


class ServiceResponse(ServiceBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int | None = None
    email: EmailStr | None = None
    users: list[ServiceUserSummary] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
