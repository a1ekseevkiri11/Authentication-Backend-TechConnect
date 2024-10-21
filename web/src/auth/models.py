import enum
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship
)
from sqlalchemy import (
    Text,
    ForeignKey,
    String,
    Enum,
)
from typing import List, Optional


from src.models import (
    Base,
)


from src.models import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        primary_key=True, 
        autoincrement=True,
    )
    
    auth_methods: Mapped[List["AuthMethod"]] = relationship()
    
    auth_methods_with_password: Mapped[List["AuthMethodWithPassword"]] = relationship()
    

class AuthMethodEnum(enum.Enum):
    TELEGRAM = "telegram"
        

class AuthMethod(Base):
    __tablename__ = "auth_methods"

    id: Mapped[int] = mapped_column(
        primary_key=True, 
        autoincrement=True,
    )
    method: Mapped[AuthMethodEnum] = mapped_column(
        Enum(AuthMethodEnum), 
        nullable=False,
    )
    identifier: Mapped[str] = mapped_column(
        String(255), 
        nullable=False,
    )
    
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
    )
    user: Mapped["User"] = relationship(
        back_populates="auth_methods",
    )
    

class AuthMethodWithPasswordEnum(enum.Enum):
    EMAIL = "email"
    TELEPHONE = "telephone"
    

class AuthMethodWithPassword(Base):
    __tablename__ = "auth_methods_with_password"
    
    id: Mapped[int] = mapped_column(
        primary_key=True, 
        autoincrement=True,
    )
    method: Mapped[AuthMethodWithPasswordEnum] = mapped_column(
        Enum(AuthMethodEnum), 
        nullable=False,
    )
    identifier: Mapped[str] = mapped_column(
        String(255), 
        nullable=False,
    )
    hashed_password: Mapped[str] = mapped_column(
        String(255), 
        nullable=False,
    )
    
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
    )
    user: Mapped["User"] = relationship(
        back_populates="auth_methods_with_password"
    )
