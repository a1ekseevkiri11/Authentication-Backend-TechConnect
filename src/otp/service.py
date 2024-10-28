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


class TempUserService:
    """
    Сервис для работы с временными пользователями.

    Методы:
    - add_temp_user: Добавляет временного пользователя с одноразовым паролем и временем жизни.
    - get: Получает временного пользователя по его идентификатору.
    """

    @staticmethod
    async def add_temp_user(
        otp_code: str,
        user_data: auth_schemas.UserCreateDB,
    ) -> int:
        """
        Добавляет временного пользователя с указанным одноразовым паролем.

        Параметры:
        - otp_code: str - Одноразовый пароль, который будет сохранен.
        - user_data: UserCreateDB - Данные пользователя для создания временного пользователя.

        Возвращает:
        - int: Идентификатор добавленного временного пользователя.
        """
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
        """
        Получает временного пользователя по его идентификатору.

        Параметры:
        - id: int - Идентификатор временного пользователя.

        Возвращает:
        - TempUser: Данные временного пользователя.

        Исключения:
        - HTTPException: Если временный пользователь не найден.
        """
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
    """
    Базовый сервис для работы с одноразовыми паролями (OTP).

    Методы:
    - _generate_code: Генерирует одноразовый пароль.
    - check_otp_code: Проверяет, соответствует ли код одноразового пароля.
    - _send_code: Отправляет одноразовый пароль (метод должен быть переопределен в дочерних классах).
    - send: Генерирует код и отправляет его пользователю.
    """

    @classmethod
    def _generate_code(self) -> int:
        """
        Генерирует одноразовый пароль.

        Возвращает:
        - int: Сгенерированный одноразовый пароль.
        """
        return "".join(
            secrets.choice(string.digits) for _ in range(settings.otp.length)
        )

    @staticmethod
    async def check_otp_code(
        temp_user_data: auth_schemas.TempUser,
        code: str,
    ) -> bool:
        """
        Проверяет, действителен ли код одноразового пароля.

        Параметры:
        - temp_user_data: TempUser - Данные временного пользователя.
        - code: str - Код для проверки.

        Возвращает:
        - bool: True, если код действителен, иначе False.
        """
        if temp_user_data.exp < datetime.now():
            return False

        return is_matched_hash(word=code, hashed=temp_user_data.otp_code)

    @classmethod
    async def _send_code(
        self,
        code: str,
        user_data: auth_schemas.UserCreateDB,
    ) -> None:
        """
        Отправляет одноразовый пароль пользователю (метод должен быть переопределен в дочерних классах).

        Параметры:
        - code: str - Код для отправки.
        - user_data: UserCreateDB - Данные пользователя для отправки.
        """
        pass

    @classmethod
    async def send(
        self,
        user_data: auth_schemas.UserCreateDB,
        background_tasks: BackgroundTasks,
    ) -> int:
        """
        Генерирует одноразовый пароль и отправляет его пользователю.

        Параметры:
        - user_data: UserCreateDB - Данные пользователя для отправки.
        - background_tasks: BackgroundTasks - Задачи, которые будут выполнены в фоновом режиме.

        Возвращает:
        - int: Идентификатор временного пользователя.
        """
        
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
    """
    Сервис для работы с одноразовыми паролями (OTP) через SMS.
    """

    @classmethod
    async def _send_code(
        self,
        code: str,
        user_data: auth_schemas.UserCreateDB,
    ) -> None:
        """
        Отправляет одноразовый пароль пользователю по SMS.

        Параметры:
        - code: str - Код для отправки.
        - user_data: UserCreateDB - Данные пользователя для отправки.
        """
        await sms_service.SMSService.send_sms(
            msg=code,
            telephone=user_data.telephone,
        )


class EmailOTPService(BaseOTPService):
    """
    Сервис для работы с одноразовыми паролями (OTP) через Email.
    """

    @classmethod
    async def _send_code(
        self,
        code: str,
        user_data: auth_schemas.UserCreateDB,
    ) -> None:
        """
        Отправляет одноразовый пароль пользователю по Email.

        Параметры:
        - code: str - Код для отправки.
        - user_data: UserCreateDB - Данные пользователя для отправки.
        """
        
        msg = MIMEText(code)
        msg["Subject"] = "Ваш одноразовый пароль"
        msg["From"] = settings.smtp.from_address
        msg["To"] = user_data.email
        await EmailService.send(msg=msg, to_adres=user_data.email)
