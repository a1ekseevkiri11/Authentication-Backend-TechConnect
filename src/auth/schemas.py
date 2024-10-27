from datetime import datetime
import re
from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    field_validator,
)
from typing import  Optional


class AbstractTelephoneForAuth(BaseModel):
    telephone: str

    @field_validator("telephone", mode="before")
    @classmethod
    def validate_name(cls, v):
        if not re.match(r"^\+7\d{10}$", v):
            raise ValueError("Номер телефона должен быть в формате +7XXXXXXXXXX")
        return v[1:]


class AbstractPasswordForAuth(BaseModel):
    password: str
    
    @field_validator("password", mode="before")
    @classmethod
    def validate_name(cls, v):
        if not(0 < len(v) < 256):
            raise ValueError("Длинна пароля должена быть больше 0 и меньше 256")
        return v


class AbstractLoginRequest(AbstractPasswordForAuth):
    pass


class EmailLoginRequest(AbstractLoginRequest):
    email: EmailStr


class TelephoneLoginRequest(AbstractTelephoneForAuth, AbstractLoginRequest):
    pass


class AbstractRegisterRequest(AbstractPasswordForAuth):
    pass


class EmailRegisterRequest(AbstractRegisterRequest):
    email: EmailStr


class TelephoneRegisterRequest(AbstractRegisterRequest, AbstractTelephoneForAuth):
    pass


class AbstractUser(BaseModel):
    email: Optional[EmailStr] = None
    telephone: Optional[str] = None
    hashed_password: str


class Telegram(BaseModel):
    id: int
    first_name: str
    last_name: Optional[str] = None
    username: str
    photo_url: str

    class Config:
        from_attributes = True


class TelegramCreateDB(BaseModel):
    id: int
    first_name: str
    last_name: Optional[str] = None
    username: str
    photo_url: str
    user_id: int


class TelegramUpdateDB(TelegramCreateDB):
    pass


class TelegramRequest(BaseModel):
    id: int
    first_name: str
    last_name: Optional[str] = None
    username: str
    photo_url: str
    auth_date: int
    hash: str


class TelegramResponse(BaseModel):
    first_name: str
    last_name: Optional[str] = None
    username: str
    photo_url: str

    class Config:
        from_attributes = True


class User(AbstractUser):
    id: int

    class Config:
        from_attributes = True


class UserCreateDB(AbstractUser):
    pass


class UserUpdateDB(UserCreateDB):
    id: int


class UserResponse(BaseModel):
    id: int
    email: Optional[EmailStr] = None
    telephone: Optional[str] = None
    telegram: Optional[TelegramResponse] = None

    class Config:
        from_attributes = True


class TempUserResponce(BaseModel):
    id: int

    
class OTPRequest(BaseModel):
    temp_user_id: int
    code: str


class TempUser(AbstractUser):
    id: int
    exp: datetime
    otp_code: str

    class Config:
        from_attributes = True


class TempUserCreateDB(AbstractUser):
    exp: datetime
    otp_code: str


class TempUserUpdateDB(TempUserCreateDB):
    id: int


class Token(BaseModel):
    access_token: str
    token_type: str = "Bearer"
