import abc
import smtplib
import secrets
import string
from email.mime.text import MIMEText
from fastapi import (
    HTTPException,
    status,
    Depends,
)
from pydantic import EmailStr


from src.settings import settings
from src.database import async_session_maker
from src.auth import dao as auth_dao
from src.auth import schemas as auth_schemas
from src.auth.utils import get_hash


class TempUserService:

    @staticmethod
    async def add_temp_user(
        otp_code: str,
        otp_type: str,
        user_data: auth_schemas.UserCreateDB,
    ) -> int:
        async with async_session_maker() as session:
            temp_user_db = await auth_dao.TempUserDao.add(
                session,
                auth_schemas.TempUserCreateDB(
                    **user_data.model_dump(),
                    otp_type=otp_type,
                    otp_code=otp_code,
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

        return temp_user_db.get_schema()

    @staticmethod
    async def delete(
        id: int,
    ) -> None:
        async with async_session_maker() as session:
            await auth_dao.TempUserDao.delete(
                session,
                id=id,
            )
            await session.commit()


class BaseOTPService(abc.ABC):
    otp_type: str

    @classmethod
    def _generate_code(self) -> int:
        return "".join(secrets.choice(string.digits) for _ in range(6))

    @classmethod
    async def check_otp_code(
        self,
        temp_user_data: auth_schemas.TempUser,
        code: str,
    ) -> bool:
        return temp_user_data.otp_code == code

    @classmethod
    async def _send_code(
        self,
        code: str,
        user_data: auth_schemas.UserCreateDB,
    ):
        pass

    @classmethod
    async def send(
        self,
        user_data: auth_schemas.UserCreateDB,
    ) -> int:
        code = self._generate_code()

        await self._send_code(
            code=code,
            user_data=user_data,
        )

        temp_user_db_id = await TempUserService.add_temp_user(
            otp_code=code,
            otp_type=self.otp_type,
            user_data=user_data,
        )

        return temp_user_db_id


# TODO: разделить email и sms отправку от OTP
# TODO: сделать отправку email и sms фоновыми задачами


class TelephoneOTPService(BaseOTPService):
    pass


class EmailOTPService(BaseOTPService):
    otp_type = "email"

    @classmethod
    async def _send_code(
        self,
        code: str,
        user_data: auth_schemas.UserCreateDB,
    ):
        msg = MIMEText(code)
        msg["Subject"] = "Ваш одноразовый пароль"
        msg["From"] = settings.email.from_address
        msg["To"] = user_data.email
        try:
            with smtplib.SMTP("smtp.yandex.ru", 587) as server:
                server.starttls()
                server.login(
                    settings.email.from_address, settings.email.from_address_password
                )
                server.sendmail(
                    settings.email.from_address, user_data.email, msg.as_string()
                )
        except Exception as e:
            print("\nERROR\n", e)
            raise HTTPException(status_code=500, detail=f"Failed to send OTP {e}")
