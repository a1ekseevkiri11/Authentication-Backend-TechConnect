from src.auth import models
from src.auth import schemas
from src import dao as auth_dao


class UserDao(
    auth_dao.BaseDAO[
        models.User,
        schemas.UserCreateDB,
        schemas.UserUpdateDB,
    ]
):
    model = models.User


class TempUserDao(
    auth_dao.BaseDAO[
        models.TempUser,
        schemas.TempUserCreateDB,
        schemas.TempUserUpdateDB,
    ]
):
    model = models.TempUser
