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
            algorithms: str = settings.auth_jwt.algorithm
    ) -> auth_schemas.Token:
        try:
            return jwt.decode(token, key=public_key, algorithms=[algorithms])
        except ValueError as ex:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Could not validate credentials: {ex}")

    @classmethod
    async def create(
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

        token = auth_schemas.Token(
            access_token=cls.encode(payload=payload)
        )

        return token


    @classmethod
    async def is_valid(
            cls,
            token: str,
    ) -> bool:
        async with async_session_maker() as session:
            token = JWTServices.decode(token=token)

            if token.exp > datetime.now():
                await cls.delete(token)
                return False
            return True
        

class UserService:
    @staticmethod
    async def add(
            user_data: auth_schemas.RegisterRequest,
            current_user_id: Optional[int] = None,
    ) -> auth_schemas.User:
        async with async_session_maker() as session:
            user_exist = await auth_dao.UserDAO.find_one_or_none(session, username=user_data.username)
            if user_exist:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="User with this username already exists"
                )

            user_exist = await auth_dao.UserDAO.find_one_or_none(session, email=user_data.email)

            if user_exist:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="User with this email already exists"
                )
            if current_user_id:
                db_user = await auth_dao.UserDAO.add(
                    session,
                    auth_schemas.UserCreateDB(
                        **user_data.model_dump(),
                        hashed_password=get_hash(user_data.password),
                        created_by=current_user_id
                    )
                )
            else:
                db_user = await auth_dao.UserDAO.add(
                    session,
                    auth_schemas.UserCreateDB(
                        **user_data.model_dump(),
                        hashed_password=get_hash(user_data.password),
                    )
                )
                db_user.created_by = db_user.id

            await session.commit()
            return db_user

    @staticmethod
    async def get(
            user_id: int
    ) -> auth_schemas.User:
        async with async_session_maker() as session:
            db_user = await auth_dao.UserDAO.find_one_or_none(
                session,
                id=user_id
            )
        if db_user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        return db_user


    @classmethod
    async def delete(
            cls,
            current_user_id: int,
            user_id: int
    ) -> None:

        async with async_session_maker() as session:
            db_user = await cls.get(user_id=user_id)
            await auth_dao.UserDAO.delete(
                session=session,
                id=user_id,
            )
            await session.commit()



class AuthService:
    @staticmethod
    async def login(
            user_data: auth_schemas.LoginRequest,
    ) -> Optional[auth_schemas.User]:
        async with async_session_maker() as session:
            db_user = await auth_dao.UserDAO.find_one_or_none(
                session,
                username=user_data.username
            )

        if db_user and is_matched_hash(
            word=user_data.password,
            hashed=db_user.hashed_password
        ):
            return db_user

        return None

    @classmethod
    async def get_current_user(
            cls,
            token: str = Depends(oauth2_scheme),
    ) -> Optional[auth_schemas.User]:
        try:
            payload = JWTServices.decode(token=token)
            if not await JWTServices.is_valid(token=token):
                raise exceptions.InvalidTokenException

            user_id = payload.get("sub")

            if user_id is None:
                raise exceptions.InvalidTokenException

        except Exception:
            raise exceptions.InvalidTokenException

        current_user = await UserService.get(user_id)

        current_user.token = token
        return current_user