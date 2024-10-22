import abc
from datetime import timedelta, datetime, timezone
import jwt
from fastapi import (
    HTTPException,
    status,
    Depends,
)
from typing import Optional


from src.settings import settings
from src.database import async_session_maker
from src.auth import schemas as auth_schemas
from src.auth import dao as auth_dao
from src import exceptions
from src.auth.utils import (
    get_hash,
    is_matched_hash,
    # OAuth2PasswordBearerWithCookie,
)


# class UserService:
#     @staticmethod
#     async def add(
#             user_data: auth_schemas.RegisterRequest,
#     ) -> auth_schemas.User:
#         async with async_session_maker() as session:
#             db_user = await auth_dao.UserDAO.add(
#                 session,
#                 auth_schemas.UserCreateDB(
#                     **user_data.model_dump(),
#                     hashed_password=get_hash(user_data.password),
#                 )
#             )
#             await session.commit()

#         return db_user


#     @staticmethod
#     async def get(
#             user_id: int
#     ) -> auth_schemas.User:
#         async with async_session_maker() as session:
#             db_user = await auth_dao.UserDAO.find_one_or_none(
#                 session,
#                 id=user_id,
#             )
#         if db_user is None:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail="User not found",
#             )
#         return db_user


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

# class AuthServiceWithPassword:
#     @staticmethod
#     async def login(
#             user_data: auth_schemas.LoginRequest,
#     ) -> Optional[auth_schemas.User]:
#         pass


# class AuthService:
#     @staticmethod
#     async def login(
#             user_data: auth_schemas.LoginRequest,
#     ) -> Optional[auth_schemas.User]:
#         async with async_session_maker() as session:
#             db_user = await auth_dao.UserDAO.find_one_or_none(
#                 session,
#                 username=user_data.username
#             )

#         if db_user and is_matched_hash(
#             word=user_data.password,
#             hashed=db_user.hashed_password
#         ):
#             return db_user

#         return None

# @classmethod
# async def get_current_user(
#         cls,
#         token: str = Depends(oauth2_scheme),
# ) -> Optional[auth_schemas.User]:
#     try:
#         payload = JWTServices.decode(token=token)
#         if not await JWTServices.is_valid(token=token):
#             raise exceptions.InvalidTokenException

#         user_id = payload.get("sub")

#         if user_id is None:
#             raise exceptions.InvalidTokenException

#     except Exception:
#         raise exceptions.InvalidTokenException

#     current_user = await UserService.get(user_id)

#     current_user.token = token
#     return current_user
