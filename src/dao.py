from typing import Any, Dict, Generic, List, Optional, TypeVar, Union
from sqlalchemy import delete, insert, select, update
from sqlalchemy.sql import func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel


from src.models import Base


ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseDAO(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Базовый класс DAO (Data Access Object) для работы с моделями базы данных.

    Параметры:
    - ModelType: Тип модели, с которой работает DAO.
    - CreateSchemaType: Тип схемы для создания новой записи.
    - UpdateSchemaType: Тип схемы для обновления существующей записи.

    Методы:
    - find_one_or_none: Находит одну запись или возвращает None.
    - find_all: Находит все записи с поддержкой фильтрации и пагинации.
    - add: Добавляет новую запись в базу данных.
    - delete: Удаляет записи из базы данных по заданным условиям.
    - update: Обновляет существующую запись в базе данных.
    - count: Подсчитывает количество записей, соответствующих заданным условиям.
    """
    
    model = None

    @classmethod
    async def find_one_or_none(
        cls, session: AsyncSession, *filter, **filter_by
    ) -> Optional[ModelType]:
        """
        Находит одну запись по заданным фильтрам или возвращает None.

        Параметры:
        - session: AsyncSession - Сессия базы данных.
        - filter: Условия фильтрации.
        - filter_by: Условия фильтрации по именам полей.

        Возвращает:
        - Optional[ModelType]: Найденная запись или None.
        """
        stmt = select(cls.model).filter(*filter).filter_by(**filter_by)
        result = await session.execute(stmt)
        return result.scalars().one_or_none()

    @classmethod
    async def find_all(
        cls,
        session: AsyncSession,
        *filter,
        offset: int = 0,
        limit: int = 100,
        **filter_by,
    ) -> List[ModelType]:
        """
        Находит все записи с поддержкой фильтрации и пагинации.

        Параметры:
        - session: AsyncSession - Сессия базы данных.
        - filter: Условия фильтрации.
        - offset: int - Смещение для пагинации (по умолчанию 0).
        - limit: int - Лимит записей для получения (по умолчанию 100).
        - filter_by: Условия фильтрации по именам полей.

        Возвращает:
        - List[ModelType]: Список найденных записей.
        """
        
        stmt = (
            select(cls.model)
            .filter(*filter)
            .filter_by(**filter_by)
            .offset(offset)
            .limit(limit)
        )
        result = await session.execute(stmt)
        return result.scalars().all()

    @classmethod
    async def add(
        cls, session: AsyncSession, obj_in: Union[CreateSchemaType, Dict[str, Any]]
    ) -> Optional[ModelType]:
        """
        Добавляет новую запись в базу данных.

        Параметры:
        - session: AsyncSession - Сессия базы данных.
        - obj_in: Union[CreateSchemaType, Dict[str, Any]] - Данные для создания записи.

        Возвращает:
        - Optional[ModelType]: Добавленная запись или None в случае ошибки.
        """
        
        if isinstance(obj_in, dict):
            create_data = obj_in
        else:
            create_data = obj_in.model_dump(exclude_unset=True)
        try:
            stmt = insert(cls.model).values(**create_data).returning(cls.model)
            result = await session.execute(stmt)
            return result.scalars().first()
        except (SQLAlchemyError, Exception) as e:
            if isinstance(e, SQLAlchemyError):
                msg = "Database Exc: Cannot insert data into table"
            elif isinstance(e, Exception):
                msg = "Unknown Exc: Cannot insert data into table"

            return None

    @classmethod
    async def delete(cls, session: AsyncSession, *filter, **filter_by) -> None:
        """
        Удаляет записи из базы данных по заданным условиям.

        Параметры:
        - session: AsyncSession - Сессия базы данных.
        - filter: Условия фильтрации.
        - filter_by: Условия фильтрации по именам полей.
        """
        
        stmt = delete(cls.model).filter(*filter).filter_by(**filter_by)
        await session.execute(stmt)

    @classmethod
    async def update(
        cls,
        session: AsyncSession,
        *where,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]],
    ) -> Optional[ModelType]:
        """
        Обновляет существующую запись в базе данных.

        Параметры:
        - session: AsyncSession - Сессия базы данных.
        - where: Условия для поиска записей, которые необходимо обновить.
        - obj_in: Union[UpdateSchemaType, Dict[str, Any]] - Данные для обновления записи.

        Возвращает:
        - Optional[ModelType]: Обновленная запись или None.
        """
        
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)

        stmt = (
            update(cls.model).where(*where).values(**update_data).returning(cls.model)
        )
        result = await session.execute(stmt)
        return result.scalars().one()

    @classmethod
    async def count(cls, session: AsyncSession, *filter, **filter_by):
        """
        Подсчитывает количество записей, соответствующих заданным условиям.

        Параметры:
        - session: AsyncSession - Сессия базы данных.
        - filter: Условия фильтрации.
        - filter_by: Условия фильтрации по именам полей.

        Возвращает:
        - int: Количество найденных записей.
        """
        
        stmt = (
            select(func.count())
            .select_from(cls.model)
            .filter(*filter)
            .filter_by(**filter_by)
        )
        result = await session.execute(stmt)
        return result.scalar()
