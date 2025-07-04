from sqlmodel import SQLModel
from .engine import creator_engine
from v1.models.qrcode import QRCode
from v1.models.student import Student


async def init_db():
    async with creator_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    await creator_engine.dispose()
