from datetime import timedelta, datetime, timezone
from fastapi.security import OAuth2PasswordBearer
import jwt
from fastapi import (
    HTTPException,
    status,
    Response,
)


from src.settings import settings
from src.auth import schemas as auth_schemas


class JWTServices:
    """
    Сервис для работы с JSON Web Tokens (JWT).
    """
    @classmethod
    def encode(
        cls,
        payload: dict,
        private_key: str = settings.auth_jwt.private_key_path.read_text(),
        algorithm: str = settings.auth_jwt.algorithm,
    ) -> str:
        """
        Кодирует данные в JWT-токен.

        Параметры:
        - payload: dict - данные, которые будут закодированы в токен.
        - private_key: str - закрытый ключ для подписи токена (по умолчанию считывается из настроек).
        - algorithm: str - алгоритм подписи (по умолчанию берется из настроек).

        Возвращает:
        - str: Закодированный JWT-токен.
        """
        return jwt.encode(payload, key=private_key, algorithm=algorithm)

    @classmethod
    def decode(
        cls,
        token: str,
        public_key: str = settings.auth_jwt.public_key_path.read_text(),
        algorithms: str = settings.auth_jwt.algorithm,
    ) -> auth_schemas.Token:
        try:
            return jwt.decode(token, key=public_key, algorithms=[algorithms])
        except ValueError as ex:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Could not validate credentials: {ex}",
            )

    @classmethod
    def create(
        cls,
        current_user_id: int,
        expire_timedelta: timedelta | None = None,
        access_expire_minutes: int = settings.auth_jwt.access_token_expire_minutes,
    ) -> auth_schemas.Token:
        """
        Создает новый JWT-токен для текущего пользователя.

        Параметры:
        - current_user_id: int - ID текущего пользователя.
        - expire_timedelta: timedelta | None - время истечения токена (по умолчанию - None).
        - access_expire_minutes: int - время истечения токена в минутах (по умолчанию считывается из настроек).

        Возвращает:
        - Token: Созданный JWT-токен.
        """

        now = datetime.now(timezone.utc)

        if expire_timedelta:
            exp = now + expire_timedelta
        else:
            exp = now + timedelta(minutes=access_expire_minutes)

        payload = {
            "sub": str(current_user_id),
            "exp": exp,
            "iat": now,
        }

        token = auth_schemas.Token(access_token=cls.encode(payload=payload))

        return token

    @classmethod
    def is_valid(
        self,
        token: str,
    ) -> bool:
        """
        Проверяет, действителен ли JWT-токен.

        Параметры:
        - token: str - JWT-токен для проверки.

        Возвращает:
        - bool: True, если токен действителен, иначе False.
        """
        exp = datetime.fromtimestamp(self.decode(token=token).get("exp"))
        return exp > datetime.now()


class TokenService:
    """
    Сервис для управления токенами в HTTP-ответах.
    """
    
    @staticmethod
    def set(response: Response, token: auth_schemas.Token) -> None:
        """
        Устанавливает JWT-токен в cookie в HTTP-ответе.

        Параметры:
        - response: Response - объект ответа для установки cookie.
        - token: Token - JWT-токен для установки в cookie.
        """
        response.set_cookie(
            "access_token",
            token.access_token,
            max_age=settings.auth_jwt.access_token_expire_minutes * 60,
            httponly=True,
        )

    @staticmethod
    def clear(
        response: Response,
    ) -> None:
        """
        Удаляет JWT-токен из cookie в HTTP-ответе.

        Параметры:
        - response: Response - объект ответа для удаления cookie.
        """
        response.delete_cookie("access_token")
