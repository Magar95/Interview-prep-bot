from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (AsyncSession, 
                                    async_sessionmaker, 
                                    create_async_engine)
from sqlalchemy.orm import declarative_base

Base = declarative_base()

# Пока используем SQLite для демонстрации (на уроке 51 заменим на PostgreSQL)
DATABASE_URL = "postgresql+asyncpg://postgres:admin123@localhost:5432/interview_prep"

engine = create_async_engine(DATABASE_URL)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Зависимость для получения сессии БД.

    FastAPI создаст сессию перед запросом
    и закроет её после ответа.
    """
    async with AsyncSessionLocal() as session:
        yield session
