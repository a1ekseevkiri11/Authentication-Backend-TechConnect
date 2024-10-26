from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import MetaData
from sqlalchemy.orm import Mapped, mapped_column


from src.settings import settings
from src.constants import DB_NAMING_CONVENTION


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=DB_NAMING_CONVENTION)
