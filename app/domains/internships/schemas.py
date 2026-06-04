from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class InternshipsBase(BaseModel):
    name: str
    region_id: int | None = None
    is_active: bool = True


class InternshipsCreate(InternshipsBase):
    user_name: str | None = None
    user_email: EmailStr | None = None


class InternshipsUpdate(BaseModel):
    name: str | None = None
    region_id: int | None = None
    is_active: bool | None = None
    user_name: str | None = None
    user_email: EmailStr | None = None


class InternshipsUserSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: EmailStr


class InternshipsResponse(InternshipsBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int | None = None
    email: EmailStr | None = None
    users: list[InternshipsUserSummary] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
