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


class UserService:

    @staticmethod
    async def add(
        session: AsyncSession,
        user_data: auth_schemas.UserCreateDB,
    ) -> auth_schemas.User:
        db_user = await auth_dao.UserDao.add(
            session,
            auth_schemas.UserCreateDB(
                **user_data.model_dump(),
            ),
        )
        await session.commit()
        return db_user

    # @staticmethod
    # async def get(
    #         user_id: int
    # ) -> auth_schemas.User:
    #     async with async_session_maker() as session:
    #         db_user = await auth_dao.UserDAO.find_one_or_none(
    #             session,
    #             id=user_id,
    #         )
    #     if db_user is None:
    #         raise HTTPException(
    #             status_code=status.HTTP_404_NOT_FOUND,
    #             detail="User not found",
    #         )
    #     return db_user

    # @classmethod
    # async def delete(
    #         cls,
    #         user_id: int
    # ) -> None:
    #     async with async_session_maker() as session:
    #         db_user = await cls.get(user_id=user_id)
    #         await auth_dao.UserDAO.delete(
    #             session=session,
    #             id=user_id,
    #         )
    #         await session.commit()
