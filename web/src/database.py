from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
)
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import MetaData


from src.settings import settings
from src.constants import DB_NAMING_CONVENTION


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=DB_NAMING_CONVENTION)
    pass


engine = create_async_engine(url=settings.db.url, echo=settings.db.echo)

async_session_maker = async_sessionmaker(
    bind=engine, autoflush=False, autocommit=False, expire_on_commit=False
)
