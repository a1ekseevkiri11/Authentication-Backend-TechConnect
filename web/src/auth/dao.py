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


class AuthMethodWithPasswordDao(
    auth_dao.BaseDAO[
        models.AuthMethodWithPassword,
        schemas.AuthMethodWithPasswordCreateDB,
        schemas.AuthMethodWithPasswordUpdateDB,
    ]
):
    model = models.AuthMethodWithPassword
