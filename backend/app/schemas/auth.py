"""Authentication request/response schemas."""

from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator


class RegisterRequest(BaseModel):

    username: str = Field(min_length=3, max_length=40)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str = Field(default="", max_length=120)

    @field_validator("username")
    @classmethod
    def _validate_username(cls, value: str) -> str:

        value = value.strip()

        if not value.replace("_", "").replace(".", "").isalnum():
            raise ValueError(
                "Username may only contain letters, numbers, '_' and '.'."
            )

        return value


class LoginRequest(BaseModel):

    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class TokenResponse(BaseModel):

    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: dict


class ForgotPasswordRequest(BaseModel):

    email: EmailStr


class ResetPasswordRequest(BaseModel):

    token: str
    new_password: str = Field(min_length=8, max_length=128)


class ChangePasswordRequest(BaseModel):

    current_password: str = Field(min_length=1, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)


class ForgotPasswordResponse(BaseModel):

    detail: str
    reset_token: Optional[str] = None
