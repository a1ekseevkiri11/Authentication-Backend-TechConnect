import asyncio
from src.auth.services.user import UserService
from src.auth.schemas import UserCreateDB
from src.database import async_session_maker


async def test_user_service_add():
    async with async_session_maker() as session:

        user_data = await UserService.get_by_email(
            email="alekseevkirill30092004@mail.ru"
        )
        print(user_data)


if __name__ == "__main__":
    asyncio.run(test_user_service_add())
