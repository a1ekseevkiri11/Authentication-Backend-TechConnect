import abc
from fastapi import (
    BackgroundTasks,
    HTTPException,
    Response,
    status,
)
from sqlalchemy import select


from src.database import async_session_maker
from src.auth import schemas as auth_schemas
from src.auth import dao as auth_dao
from src.auth import models as auth_models
from src.otp.service import (
    BaseOTPService,
    EmailOTPService,
    TelephoneOTPService,
    TempUserService,
)
from src.auth.utils import get_hash, is_matched_hash
from src.auth.services.jwt import JWTServices, TokenService


class AuthMethodWithPassword(abc.ABC):
    OTPServis: BaseOTPService = None

    @classmethod
    async def get_user(
        self, register_data: auth_schemas.AbstractRegisterRequest
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

            await auth_dao.TempUserDao.delete(session=session, id=temp_user_data.id)

            user_db = await auth_dao.UserDao.add(
                session,
                auth_schemas.UserCreateDB(**temp_user_data.model_dump(), telegram=None),
            )
            await session.commit()

        return auth_schemas.User.model_validate(user_db)

    @classmethod
    async def find_user_and_check_password(
        self, login_data: auth_schemas.AbstractLoginRequest
    ):
        user_data = await self.get_user(user_data=login_data)

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
        async with async_session_maker() as session:
            user = await auth_dao.UserDao.find_one_or_none(
                session=session,
                email=user_data.email,
            )
            if user is not None:
                return auth_schemas.User.model_validate(user)

            return None


class TelephoneAuthMethodWithPassword(AuthMethodWithPassword):
    OTPServis = TelephoneOTPService

    @classmethod
    async def get_user(self, user_data: auth_schemas.UserCreateDB) -> auth_schemas.User:
        async with async_session_maker() as session:
            user = await auth_dao.UserDao.find_one_or_none(
                session=session,
                telephone=user_data.telephone,
            )
            if user is not None:
                return auth_schemas.User.model_validate(user)

            return None


class AuthService:
    def __init__(
        self,
        method_auth: AuthMethodWithPassword,
    ) -> None:
        self._method_auth = method_auth

    async def register(
        self,
        register_data: auth_schemas.AbstractRegisterRequest,
        background_tasks: BackgroundTasks,
    ) -> int:
        user_data = auth_schemas.UserCreateDB(
            **register_data.model_dump(),
            hashed_password=get_hash(register_data.password),
        )

        if await self._method_auth.get_user(user_data=user_data) is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this identifier already exists",
            )

        temp_user_db_id = await self._method_auth.OTPServis.send(
            user_data=user_data,
            background_tasks=background_tasks,
        )

        return temp_user_db_id

    async def otp(
        self,
        temp_user_db_id: int,
        code: str,
    ):
        temp_user_db = await TempUserService.get(id=temp_user_db_id)

        if not await BaseOTPService.check_otp_code(
            temp_user_data=temp_user_db, code=code
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorect code",
            )

        user_data = await self._method_auth.create_user_from_temp_user(
            temp_user_data=temp_user_db,
        )
        return user_data

    async def login(
        self,
        response: Response,
        login_data: auth_schemas.AbstractRegisterRequest,
    ) -> auth_schemas.Token:

        user_data = await self._method_auth.find_user_and_check_password(
            login_data=login_data
        )

        token = JWTServices.create(current_user_id=user_data.id)

        TokenService.set(response=response, token=token)

        return token


EmailAuthService = AuthService(method_auth=EmailAuthMethodWithPassword)


TelephoneAuthService = AuthService(method_auth=TelephoneAuthMethodWithPassword)


class TelegramService:
    async def attach(
        telegram_request: auth_schemas.TelegramRequest, current_user: auth_schemas.User
    ) -> None:
        async with async_session_maker() as session:
            existing_telegram = await session.execute(
                select(auth_models.Telegram).where(
                    auth_models.Telegram.user_id == current_user.id
                )
            )
            if existing_telegram.scalars().first() is not None:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="User already attach telegram",
                )

            await auth_dao.TelegramDao.add(
                session,
                auth_schemas.TelegramCreateDB(
                    **telegram_request.model_dump(),
                    user_id=current_user.id,
                ),
            )

            await session.commit()


class TelegramAuthService:
    async def attach(
        telegram_request: auth_schemas.TelegramRequest, current_user: auth_schemas.User
    ) -> None:

        await TelegramService.attach(
            telegram_request=telegram_request,
            current_user=current_user,
        )
