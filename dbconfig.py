from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlmodel import SQLModel

from envconfig import EnvFile

DB_URL_USER = (
    f"mysql+asyncmy://{EnvFile.DB_USER}:"
    f"{EnvFile.DB_USER_PASSWORD}@"
    f"{EnvFile.DB_HOST}:{EnvFile.DB_PORT}/"
    f"{EnvFile.DB_NAME}"
)
DB_URL_CREATOR = (
    f"mysql+asyncmy://{EnvFile.DB_TABLE_CREATOR}:"
    f"{EnvFile.DB_TABLE_CREATOR_PASSWORD}@"
    f"{EnvFile.DB_HOST}:{EnvFile.DB_PORT}/"
    f"{EnvFile.DB_NAME}"
)

creator_engine = create_async_engine(DB_URL_CREATOR, echo=True)
user_engine = create_async_engine(DB_URL_USER, echo=True)

async_session = async_sessionmaker(
    user_engine, class_=AsyncSession, expire_on_commit=False
)


async def init_db():
    async with creator_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    await creator_engine.dispose()


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session
