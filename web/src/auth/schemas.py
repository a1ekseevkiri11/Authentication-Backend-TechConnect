from pydantic import (
    BaseModel,
    EmailStr,
)
from typing import Optional


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    c_password: str


class User(BaseModel):
    id: int
    email: EmailStr
    

class UserCreateDB(BaseModel):
    email: EmailStr
    hashed_password: str


class UserUpdateDB(BaseModel):
    email: Optional[EmailStr] = None

    
class UserRequest(BaseModel):
    username: str
    email: EmailStr
    

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    

class Token(BaseModel):
    access_token: str
    token_type: str = "Bearer"