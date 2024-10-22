import enum
from pydantic import (
    BaseModel,
    EmailStr,
)
from typing import Optional


class LoginRequest(BaseModel):
    identifier: str
    password: str


class AbstractRegisterWithPasswordRequest(BaseModel):
    method: str = None
    identifier: str
    hashed_password: str
    user_id: int = None


class EmailRegisterRequest(AbstractRegisterWithPasswordRequest):
    identifier: EmailStr


class User(BaseModel):
    id: int


class UserCreateDB(BaseModel):
    pass


class UserUpdateDB(BaseModel):
    id: int


class UserRequest(BaseModel):
    pass


class UserResponse(BaseModel):
    id: int


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    c_password: str


class AuthMethodWithPasswordEnum(str, enum.Enum):
    EMAIL = "email"
    TELEPHONE = "telephone"


class AuthMethodWithPasswordCreateDB(BaseModel):
    method: AuthMethodWithPasswordEnum
    identifier: str
    hashed_password: str
    user_id: int


class AuthMethodWithPasswordUpdateDB(BaseModel):
    id: int
    method: AuthMethodWithPasswordEnum
    identifier: str
    hashed_password: str
    user_id: int


class AuthMethodWithPassword(BaseModel):
    id: int
    method: AuthMethodWithPasswordEnum
    identifier: str
    hashed_password: str
    user_id: int


class AuthMethodEnum(str, enum.Enum):
    TELEGRAM = "telegram"


class Token(BaseModel):
    access_token: str
    token_type: str = "Bearer"
