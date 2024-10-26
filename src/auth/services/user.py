from fastapi import (
    HTTPException,
    status,
    Depends,
)
from sqlalchemy import select
from sqlalchemy.orm import selectinload


from src.database import async_session_maker
from src.auth import schemas as auth_schemas
from src.auth import dao as auth_dao
from src.auth.services.jwt import JWTServices
from src import exceptions
from src.auth.utils import OAuth2PasswordCookie


oauth2_scheme = OAuth2PasswordCookie(
    tokenUrl="/api/auth/login/",
)


class UserService:
    @staticmethod
    async def get(id: int) -> auth_schemas.User:
        async with async_session_maker() as session:
            stmt = (
                select(auth_dao.UserDao.model)
                .options(selectinload(auth_dao.UserDao.model.telegram))
                .where(auth_dao.UserDao.model.id == id)
            )
            user_db = await session.execute(stmt)
            user_db = user_db.scalars().one_or_none()

            if user_db is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
                )

        return auth_schemas.UserResponse.model_validate(user_db)

    @classmethod
    async def get_me(
        self,
        token: str = Depends(oauth2_scheme),
    ):
        try:
            if not JWTServices.is_valid(token=token):
                raise exceptions.TokenExpiredException

            payload = JWTServices.decode(token=token)
            user_id = payload.get("sub")
            if user_id is None:
                raise exceptions.InvalidTokenException

        except Exception as ex:
            raise exceptions.InvalidTokenException

        return await UserService.get(user_id)
