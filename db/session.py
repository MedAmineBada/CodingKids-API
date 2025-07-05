"""
Asynchronous Session Factory Module
"""

from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from typing import AsyncGenerator
from .engine import user_engine

# Session Factory Configuration, creates a session with user `user_engine`.
async_session = async_sessionmaker(
    user_engine, class_=AsyncSession, expire_on_commit=False
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session
