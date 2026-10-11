from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.pool import NullPool

from shared.config import DATABASE_URL


class Base(DeclarativeBase):
    pass


engine = create_engine(
    DATABASE_URL,
    poolclass=NullPool,
    connect_args={
        "sslmode": "require",
        "prepare_threshold": None,
    },
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_session():
    """Вернуть новую сессию БД."""
    return SessionLocal()