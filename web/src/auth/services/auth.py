import abc
from fastapi import (
    BackgroundTasks,
    HTTPException,
    Response,
    status,
)


from src.settings import settings
from src.database import async_session_maker
from src.auth import schemas as auth_schemas
from src.auth import dao as auth_dao
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
                
            await auth_dao.TempUserDao.delete(
                session=session,
                id=temp_user_data.id
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
    async def find_user_and_check_password(self, login_data: auth_schemas.AbstractLoginRequest):
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
            return await auth_dao.UserDao.find_one_or_none(
                session=session,
                email=user_data.email,
            )


class TelephoneAuthMethodWithPassword(AuthMethodWithPassword):
    OTPServis = TelephoneOTPService

    @classmethod
    async def get_user(self, user_data: auth_schemas.UserCreateDB) -> auth_schemas.User:
        return await auth_dao.UserDao.find_one_or_none(telephone=user_data.telephone)


class AuthService:
    def __init__(
        self,
        method_auth: AuthMethodWithPassword,
    ) -> None:
        self.method_auth = method_auth


    async def register(
        self, 
        register_data: auth_schemas.AbstractRegisterRequest,
        background_tasks: BackgroundTasks,
    ) -> int:
        user_data = auth_schemas.UserCreateDB(
            **register_data.model_dump(),
        )

        user_data.hashed_password = get_hash(register_data.password)

        if await self.method_auth.get_user(user_data=user_data) is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this identifier already exists",
            )

        temp_user_db_id = await self.method_auth.OTPServis.send(
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
        
        if not await self.method_auth.OTPServis.check_otp_code(
            temp_user_data=temp_user_db, code=code
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorect code",
            )

        user_data = await self.method_auth.create_user_from_temp_user(
            temp_user_data=temp_user_db,
        )
        return user_data
    
    
    async def login(
        self, 
        response: Response, 
        login_data: auth_schemas.AbstractRegisterRequest,
    ) -> auth_schemas.Token:

        user_data = await self.method_auth.find_user_and_check_password(
            login_data=login_data
        )

        token = JWTServices.create(current_user_id=user_data.id)

        TokenService.set(response=response, token=token)

        return token


EmailAuthService = AuthService(
    method_auth=EmailAuthMethodWithPassword
)
