import enum
import re
from pydantic import (
    BaseModel,
    EmailStr,
    ValidationError,
    field_validator,
    model_validator,
)
from pydantic_extra_types.phone_numbers import PhoneNumber
from typing import Annotated, Optional, Self


class AbstractLoginRequest(BaseModel):
    password: str


class EmailLoginRequest(AbstractLoginRequest):
    email: EmailStr


class AbstractRegisterRequest(BaseModel):
    password: str


class EmailRegisterRequest(AbstractRegisterRequest):
    email: EmailStr


class User(BaseModel):
    id: int
    email: EmailStr | None = None
    telephone: str | None = None
    telegram_id: str | None = None
    hashed_password: str | None = None


class UserCreateDB(BaseModel):
    email: EmailStr | None = None
    telephone: str | None = None
    telegram_id: str | None = None
    hashed_password: str | None = None


class UserUpdateDB(BaseModel):
    id: int
    email: EmailStr | None = None
    telephone: str | None = None
    telegram_id: str | None = None
    hashed_password: str | None = None


class UserResponse(BaseModel):
    id: int
    email: EmailStr | None = None
    telephone: str | None = None
    telegram_id: str | None = None


class TempUser(User):
    otp_type: str
    otp_code: str


class TempUserCreateDB(UserCreateDB):
    otp_type: str
    otp_code: str


class TempUserUpdateDB(UserUpdateDB):
    otp_type: str
    otp_code: str


class Token(BaseModel):
    access_token: str
    token_type: str = "Bearer"
