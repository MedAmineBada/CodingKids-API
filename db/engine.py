from sqlalchemy.ext.asyncio import create_async_engine
from envconfig import EnvFile

DB_URL_USER = (
    f"mysql+asyncmy://{EnvFile.DB_USER}:{EnvFile.DB_USER_PASSWORD}@"
    f"{EnvFile.DB_HOST}:{EnvFile.DB_PORT}/{EnvFile.DB_NAME}"
)
DB_URL_CREATOR = (
    f"mysql+asyncmy://{EnvFile.DB_TABLE_CREATOR}:{EnvFile.DB_TABLE_CREATOR_PASSWORD}@"
    f"{EnvFile.DB_HOST}:{EnvFile.DB_PORT}/{EnvFile.DB_NAME}"
)

creator_engine = create_async_engine(DB_URL_CREATOR, echo=True)
user_engine = create_async_engine(DB_URL_USER, echo=True)
