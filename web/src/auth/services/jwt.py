from datetime import timedelta, datetime, timezone
from fastapi.security import OAuth2PasswordBearer
import jwt
from fastapi import (
    HTTPException,
    status,
    Depends,
    Response,
)
from typing import Optional


from src.settings import settings
from src.database import async_session_maker
from src.auth import schemas as auth_schemas

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login/")


class JWTServices:
    @classmethod
    def encode(
        cls,
        payload: dict,
        private_key: str = settings.auth_jwt.private_key_path.read_text(),
        algorithm: str = settings.auth_jwt.algorithm,
    ) -> str:
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
        exp = datetime.fromtimestamp(self.decode(token=token).get("exp"))
        return exp > datetime.now()


class TokenService:
    @staticmethod
    def set(response: Response, token: auth_schemas.Token) -> None:
        response.set_cookie(
            "access_token",
            token.access_token,
            max_age=settings.auth_jwt.access_token_expire_minutes,
            httponly=True,
        )

    @staticmethod
    def clear(
        response: Response,
    ) -> None:
        pass
