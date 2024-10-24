from fastapi import (
    HTTPException,
    status,
    Depends,
)


from src.settings import settings
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
            user_db = await auth_dao.UserDao.find_one_or_none(
                session,
                id=id,
            )
            if user_db is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
                )
        return user_db.get_schema()

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

        user_data = await UserService.get(user_id)
        return user_data
