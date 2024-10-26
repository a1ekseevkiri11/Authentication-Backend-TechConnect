from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
)


from src.settings import settings


engine = create_async_engine(url=settings.db.url, echo=settings.db.echo)

async_session_maker = async_sessionmaker(
    bind=engine, autoflush=False, autocommit=False, expire_on_commit=False
)
