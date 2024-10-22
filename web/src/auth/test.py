import asyncio
from src.auth.services.user import UserService
from src.auth.schemas import UserCreateDB
from src.database import async_session_maker


async def test_user_service_add():
    async with async_session_maker() as session:
        # Пример тестовых данных пользователя
        test_user_data = UserCreateDB()

        created_user = await UserService.add(session, test_user_data)

        if created_user:
            print("Пользователь успешно создан:")
            print(created_user.id)
        else:
            print("Ошибка создания пользователя")


if __name__ == "__main__":
    asyncio.run(test_user_service_add())
