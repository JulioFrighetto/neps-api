from datetime import datetime
from typing import Literal

from pydantic import AliasChoices, BaseModel, ConfigDict, EmailStr, Field, model_validator


UserRole = Literal["admin", "education_institute", "internships"]


class UserBase(BaseModel):
    name: str
    email: EmailStr
    is_active: bool = True


class UserCreate(UserBase):
    password: str | None = None
    role: UserRole
    internships_id: int | None = Field(default=None, alias="internship_id")
    education_institute_id: int | None = None

    @model_validator(mode="after")
    def validate_profile_links(self):
        if self.role == "admin":
            if (
                self.internships_id is not None
                or self.education_institute_id is not None
            ):
                raise ValueError("Admin não deve ser vinculado a instituição de ensino ou unidade")
        elif self.role == "internships":
            if self.internships_id is None:
                raise ValueError("Usuário de internships precisa de internships vinculada")
            if self.education_institute_id is not None:
                raise ValueError("Usuário de internships não pode ser vinculado a instituição de ensino")
        elif self.role == "education_institute":
            if self.education_institute_id is None:
                raise ValueError("Usuário de entidade de ensino precisa de instituição vinculada")
            if self.internships_id is not None:
                raise ValueError("Usuário de entidade de ensino não pode ser vinculado a unidade")
        return self


class UserUpdate(BaseModel):
    name: str | None = None
    email: EmailStr | None = None
    is_active: bool | None = None


class UserChangePassword(BaseModel):
    current_password: str
    new_password: str


class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    role: str
    internships_id: int | None = Field(default=None, alias="internship_id")
    education_institute_id: int | None = None
    created_at: datetime
    updated_at: datetime


# ── Auth ──────────────────────────────────────────────────────────────────────

class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirmRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    reset_hash: str = Field(
        validation_alias=AliasChoices("hash", "reset_hash", "reset_token"),
        serialization_alias="hash",
    )
    new_password: str


class TestEmailRequest(BaseModel):
    email: EmailStr
