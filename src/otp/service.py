import abc
from datetime import datetime, timedelta
import secrets
import string
from email.mime.text import MIMEText
from fastapi import (
    HTTPException,
    status,
    BackgroundTasks,
)


from src.settings import settings
from src.database import async_session_maker
from src.auth import dao as auth_dao
from src.auth import schemas as auth_schemas
from src.auth.utils import get_hash, is_matched_hash
from src.sms import service as sms_service
from src.email.service import EmailService


# TODO переместить схемы и модели TempUser в эту директорию
class TempUserService:

    @staticmethod
    async def add_temp_user(
        otp_code: str,
        user_data: auth_schemas.UserCreateDB,
    ) -> int:
        async with async_session_maker() as session:
            hashed_otp_code = get_hash(otp_code)
            exp = datetime.now() + timedelta(minutes=settings.otp.expire_minutes)
            temp_user_db = await auth_dao.TempUserDao.add(
                session,
                auth_schemas.TempUserCreateDB(
                    **user_data.model_dump(),
                    exp=exp,
                    otp_code=hashed_otp_code,
                ),
            )
            await session.commit()

        return temp_user_db.id

    @staticmethod
    async def get(
        id: int,
    ):
        async with async_session_maker() as session:
            temp_user_db = await auth_dao.TempUserDao.find_one_or_none(
                session,
                id=id,
            )

            if temp_user_db is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Temp user not found"
                )

        return auth_schemas.TempUser.model_validate(temp_user_db)


class BaseOTPService(abc.ABC):

    @classmethod
    def _generate_code(self) -> int:
        return "".join(
            secrets.choice(string.digits) for _ in range(settings.otp.length)
        )

    @staticmethod
    async def check_otp_code(
        temp_user_data: auth_schemas.TempUser,
        code: str,
    ) -> bool:
        if temp_user_data.exp < datetime.now():
            return False

        return is_matched_hash(word=code, hashed=temp_user_data.otp_code)

    @classmethod
    async def _send_code(
        self,
        code: str,
        user_data: auth_schemas.UserCreateDB,
    ) -> None:
        pass

    @classmethod
    async def send(
        self,
        user_data: auth_schemas.UserCreateDB,
        background_tasks: BackgroundTasks,
    ) -> int:
        code = self._generate_code()

        background_tasks.add_task(
            self._send_code,
            code=code,
            user_data=user_data,
        )

        temp_user_db_id = await TempUserService.add_temp_user(
            otp_code=code,
            user_data=user_data,
        )

        return temp_user_db_id


class TelephoneOTPService(BaseOTPService):

    @classmethod
    async def _send_code(
        self,
        code: str,
        user_data: auth_schemas.UserCreateDB,
    ) -> None:
        await sms_service.SMSService.send_sms(
            msg=code,
            telephone=user_data.telephone,
        )


class EmailOTPService(BaseOTPService):

    @classmethod
    async def _send_code(
        self,
        code: str,
        user_data: auth_schemas.UserCreateDB,
    ) -> None:
        msg = MIMEText(code)
        msg["Subject"] = "Ваш одноразовый пароль"
        msg["From"] = settings.smtp.from_address
        msg["To"] = user_data.email
        await EmailService.send(msg=msg, to_adres=user_data.email)
