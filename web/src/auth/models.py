import enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Text, ForeignKey, String, Enum, Integer
from typing import List, Optional
from src.auth import schemas as auth_schemas


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

    email: Mapped[str] = mapped_column(
        String(255),
        nullable=True,
    )

    telephone: Mapped[str] = mapped_column(
        String(20),
        nullable=True,
    )

    telegram_id: Mapped[str] = mapped_column(
        String(255),
        nullable=True,
    )

    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=True,
    )

    def get_schema(self) -> auth_schemas.User:
        return auth_schemas.User(
            id=self.id,
            email=self.email,
            telephone=self.telephone,
            telegram_id=self.telegram_id,
            hashed_password=self.hashed_password,
        )


class TempUser(Base):
    __tablename__ = "temp_users"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    otp_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    otp_code: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        nullable=True,
    )

    telephone: Mapped[str] = mapped_column(
        String(20),
        nullable=True,
    )

    telegram_id: Mapped[str] = mapped_column(
        String(255),
        nullable=True,
    )

    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=True,
    )

    def get_schema(self) -> auth_schemas.TempUser:
        return auth_schemas.TempUser(
            id=self.id,
            email=self.email,
            otp_type=self.otp_type,
            otp_code=self.otp_code,
            telephone=self.telephone,
            telegram_id=self.telegram_id,
            hashed_password=self.hashed_password,
        )
