from typing import Any, Dict, Generic, List, Optional, TypeVar, Union
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession


from src.settings import settings
from src.database import async_session_maker
from src.auth import schemas as auth_schemas
from src.auth import dao as auth_dao
from src.auth.services.jwt import JWTServices
from src import exceptions
from src.auth.utils import OAuth2PasswordCookie


oauth2_scheme = OAuth2PasswordCookie(
    tokenUrl="/api/auth/login/",
)


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
        return db_user.get_schema()

    @staticmethod
    async def get(id: int) -> auth_schemas.User:
        async with async_session_maker() as session:
            user_db = await auth_dao.UserDao.find_one_or_none(
                session,
                id=id,
            )
            if user_db:
                return user_db.get_schema()

        return None

    @classmethod
    async def get_me(
        self,
        token: str = Depends(oauth2_scheme),
    ):
        try:
            if not JWTServices.is_valid(token=token):
                raise exceptions.TokenExpiredException

            payload = JWTServices.decode(token=token)
            user_id = payload.get("sub")
            if user_id is None:
                raise exceptions.InvalidTokenException

        except Exception as ex:
            raise ex

        user_data = await UserService.get(user_id)
        return user_data

    @staticmethod
    async def get_by_email(email: str) -> auth_schemas.User:
        async with async_session_maker() as session:
            user_db = await auth_dao.UserDao.find_one_or_none(session, email=email)
            if user_db:
                return user_db.get_schema()

        return None

    @staticmethod
    async def get_by_telephone(telephone: str) -> auth_schemas.User:
        async with async_session_maker() as session:
            user_db = await auth_dao.UserDao.find_one_or_none(
                session, telephone=telephone
            )
            if user_db:
                return user_db.get_schema()

        return None

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
