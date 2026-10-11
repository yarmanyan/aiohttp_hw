"""Модуль для работы с базой данных (асинхронный SQLAlchemy)."""

import atexit
import datetime
import os

from dotenv import load_dotenv
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.ext.asyncio import (
    AsyncAttrs,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

load_dotenv()


POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "dbpass")
POSTGRES_DB = os.getenv("POSTGRES_DB", "app")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "127.0.0.1")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5431")

POSTGRES_DSN = (
    f"postgresql+asyncpg://"
    f"{POSTGRES_USER}:{POSTGRES_PASSWORD}@"
    f"{POSTGRES_HOST}:{POSTGRES_PORT}/"
    f"{POSTGRES_DB}"
)

engine = create_async_engine(POSTGRES_DSN)
Session = async_sessionmaker(bind=engine, expire_on_commit=False)


class Base(DeclarativeBase, AsyncAttrs):
    """Базовый класс для всех моделей."""


class User(Base):
    """Модель пользователя."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True)
    password: Mapped[str] = mapped_column(String)
    registration_time: Mapped[datetime.datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
    )

    @property
    def id_dict(self) -> dict:
        """Возвращает словарь с id пользователя."""
        return {"id": self.id}

    @property
    def dict(self) -> dict:
        """Возвращает словарь с данными пользователя."""
        return {
            "id": self.id,
            "name": self.name,
            "registration_time": int(self.registration_time.timestamp()),
        }


class Advertisement(Base):
    """Модель объявления."""

    __tablename__ = "advertisements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
    )
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    owner: Mapped["User"] = relationship("User", backref="advertisements")

    @property
    def id_dict(self) -> dict:
        """Возвращает словарь с id объявления."""
        return {"id": self.id}

    @property
    def dict(self) -> dict:
        """Возвращает словарь с данными объявления."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "created_at": int(self.created_at.timestamp()),
            "owner": self.owner_id,
        }


async def init_db() -> None:
    """Создаёт таблицы при старте приложения."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """Закрывает соединение с БД при остановке."""
    await engine.dispose()


atexit.register(lambda: print("DB closed"))