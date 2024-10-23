import abc
from datetime import timedelta, datetime, timezone
from fastapi.security import OAuth2PasswordBearer
import jwt
from fastapi import (
    HTTPException,
    Response,
    status,
    Depends,
)
from pydantic import (
    BaseModel,
    EmailStr,
    ValidationError,
)
from typing import Any, Dict, Generic, List, Optional, TypeVar, Union
from sqlalchemy.ext.asyncio import AsyncSession


from src.settings import settings
from src.database import async_session_maker
from src.auth import schemas as auth_schemas
from src.auth import dao as auth_dao
from src.auth.services.user import UserService
from src.otp.service import (
    BaseOTPService,
    EmailOTPService,
    TelephoneOTPService,
    TempUserService,
)
from src.auth.utils import get_hash, is_matched_hash
from src.auth.services.jwt import JWTServices, TokenService


def is_email(word: str) -> bool:
    try:
        _ = EmailStr._validate(word)
        return True

    except ValidationError:
        return False


def is_telefon(word: str) -> bool:
    return False


class AuthMethodWithPassword(abc.ABC):
    OTPServis: BaseOTPService = None

    @classmethod
    async def get_user_schema(self, schema) -> auth_schemas.UserCreateDB:
        pass

    @classmethod
    async def get_user(
        self, register_data: auth_schemas.RegisterWithPasswordRequest
    ) -> auth_schemas.User:
        pass

    @classmethod
    async def create_user_from_temp_user(
        self,
        temp_user_data: auth_schemas.TempUser,
    ) -> auth_schemas.User:
        async with async_session_maker() as session:

            if await self.get_user(user_data=temp_user_data) is not None:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="User with this identifier already exists",
                )

            user_db = await auth_dao.UserDao.add(
                session,
                auth_schemas.UserCreateDB(
                    **temp_user_data.model_dump(),
                ),
            )
            await session.commit()

        return user_db.get_schema()

    @classmethod
    async def find_user_and_check_password(self, login_data: auth_schemas.LoginRequest):
        async with async_session_maker() as session:
            user_data = await self.get_user_schema(login_data)
            user_data = await self.get_user(user_data=user_data)

            if not (
                user_data
                and is_matched_hash(
                    word=login_data.password, hashed=user_data.hashed_password
                )
            ):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Incorrect identifier or password",
                )

        return user_data


class EmailAuthMethodWithPassword(AuthMethodWithPassword):
    OTPServis = EmailOTPService

    @classmethod
    async def get_user(self, user_data: auth_schemas.UserCreateDB) -> auth_schemas.User:
        return await UserService.get_by_email(email=user_data.email)

    @classmethod
    async def get_user_schema(self, schema) -> auth_schemas.UserCreateDB:
        return auth_schemas.UserCreateDB(
            **schema.model_dump(),
            email=schema.identifier,
        )


class TelephoneAuthMethodWithPassword(AuthMethodWithPassword):
    OTPServis = TelephoneOTPService

    @classmethod
    async def get_user(self, user_data: auth_schemas.UserCreateDB) -> auth_schemas.User:
        return await UserService.get_by_telephone(telephone=user_data.telephone)

    @classmethod
    async def get_user_schema(self, schema) -> auth_schemas.UserCreateDB:
        return auth_schemas.UserCreateDB(
            **schema.model_dump(),
            telephon=schema.identifier,
        )


class AuthService:
    @staticmethod
    async def _get_auth_method_from_identifier(
        identifier: str,
    ) -> AuthMethodWithPassword:
        if is_email(word=identifier):
            return EmailAuthMethodWithPassword
        elif is_telefon(word=identifier):
            pass
        else:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Input Email or telefon",
            )

    @staticmethod
    async def _get_auth_method_from_otp_type(
        otp_type: str,
    ) -> AuthMethodWithPassword:
        if otp_type == EmailAuthMethodWithPassword.OTPServis.otp_type:
            return EmailAuthMethodWithPassword
        # TODO добавить телефон
        else:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Input Email or telefon",
            )

    @classmethod
    async def register(
        self, register_data: auth_schemas.RegisterWithPasswordRequest
    ) -> int:
        method_auth = await self._get_auth_method_from_identifier(
            register_data.identifier
        )
        user_data = await method_auth.get_user_schema(register_data)

        user_data.hashed_password = get_hash(register_data.password)

        if await method_auth.get_user(user_data=user_data) is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this identifier already exists",
            )

        user_db = await method_auth.OTPServis.send(user_data=user_data)

        return user_db

    @classmethod
    async def otp(
        self,
        temp_user_db_id: int,
        code: str,
    ):
        temp_user_db = await TempUserService.get(id=temp_user_db_id)
        method_auth = await self._get_auth_method_from_otp_type(
            otp_type=temp_user_db.otp_type
        )

        if not await method_auth.OTPServis.check_otp_code(
            temp_user_data=temp_user_db, code=code
        ):
            return HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorect code",
            )

        user_data = await method_auth.create_user_from_temp_user(
            temp_user_data=temp_user_db,
        )
        return user_data

        # TODO Вернуть токен

    @classmethod
    async def login(
        self, response: Response, login_data: auth_schemas.LoginRequest
    ) -> auth_schemas.Token:

        method_auth = await self._get_auth_method_from_identifier(login_data.identifier)

        user_data = await method_auth.find_user_and_check_password(
            login_data=login_data
        )

        token = JWTServices.create(current_user_id=user_data.id)

        TokenService.set(response=response, token=token)

        return token
