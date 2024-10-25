import enum
from sqlalchemy.orm import Mapped, mapped_column, relationship, mapper
from sqlalchemy import BigInteger, Text, ForeignKey, String, Enum, Integer
from typing import List, Optional
from src.auth import schemas as auth_schemas


from src.models import (
    Base,
)


from src.models import Base


class AbstractUser(Base):
    __abstract__ = True
    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )
    
    email: Mapped[str] = mapped_column(
        String(255),
        nullable=True,
    )

    telephone: Mapped[str] = mapped_column(
        String(20),
        nullable=True,
    )

    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=True,
    )


class Telegram(Base):
    __tablename__ = "telegrams"
    
    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True
    )
    first_name: Mapped[str] = mapped_column(
        String(255), 
        nullable=False
    )
    last_name: Mapped[str] = mapped_column(
        String(255), 
        nullable=True
    )
    username: Mapped[str] = mapped_column(
        String(255), 
        nullable=False
    ) 
    photo_url: Mapped[str] = mapped_column(
        String(2048), 
        nullable=False
    )
    
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped["User"] = relationship(
        "User", 
        back_populates="telegram"
    )


class User(AbstractUser):
    __tablename__ = "users"
    
    telegram: Mapped["Telegram"] = relationship(
        "Telegram", 
        back_populates="user"
    )
        

class TempUser(AbstractUser):
    __tablename__ = "temp_users"
    
    otp_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    otp_code: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )