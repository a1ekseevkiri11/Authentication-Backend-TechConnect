import abc
from datetime import timedelta, datetime, timezone
import jwt
from fastapi import (
    HTTPException,
    status,
    Depends,
)
from pydantic import (
    BaseModel,
)
from typing import Any, Dict, Generic, List, Optional, TypeVar, Union
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext


from src.settings import settings
from src.database import async_session_maker
from src.auth import schemas as auth_schemas
from src.auth import dao as auth_dao
from src.auth import models as auth_models
from src import exceptions
from src.auth.utils import (
    get_hash,
    is_matched_hash,
    # OAuth2PasswordBearerWithCookie,
)
from src.dao import BaseDAO


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_hash(word: str) -> str:
    return pwd_context.hash(word)


def is_matched_hash(word: str, hashed: str) -> bool:
    return pwd_context.verify(word, hashed)


BaseDaoType = TypeVar("BaseDaoType", bound=BaseDAO)
SchemaType = TypeVar("SchemaType", bound=BaseModel)


class InterfaceAuthMethod(Generic[SchemaType]):
    dao: BaseDaoType = None
    method: str = None

    @classmethod
    async def register(self):
        pass

    @classmethod
    async def login(self):
        pass


class AuthMethodWithPassword(InterfaceAuthMethod[auth_schemas.AuthMethodWithPassword]):
    dao = auth_dao.AuthMethodWithPasswordDao

    @classmethod
    async def register(
        self, register_data: auth_schemas.AbstractRegisterWithPasswordRequest
    ) -> auth_schemas.UserResponse:
        async with async_session_maker() as session:
            user_exist = await self.dao.find_one_or_none(
                session, method=self.method, identifier=register_data.identifier
            )
            if user_exist is not None:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="User with this identifier already exists",
                )

            # TODO если передаеться register_data.user_id, то не создавать пользователя
            user_data = auth_schemas.UserCreateDB()

            user_db = await auth_dao.UserDao.add(
                session,
                auth_schemas.UserCreateDB(
                    **user_data.model_dump(),
                ),
            )
            register_data.hashed_password = get_hash(register_data.hashed_password)
            register_data.user_id = user_db.id
            register_data.method = self.method
            await self.dao.add(session, register_data)
            await session.commit()

            return user_db

    @classmethod
    async def login(self, login_data: auth_schemas.LoginRequest):
        async with async_session_maker() as session:
            user_db = await self.dao.find_one_or_none(
                session, method=self.method, identifier=login_data.identifier
            )
            if not (
                user_db
                and is_matched_hash(
                    word=login_data.password, hashed=user_db.hashed_password
                )
            ):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Incorrect identifier or password",
                )

            return user_db

        return None


class EmailAuthMethodWithPassword(AuthMethodWithPassword):
    method = auth_schemas.AuthMethodWithPasswordEnum.EMAIL
