"""
Asynchronous Database Engines Module

Defines two SQLAlchemy async engines:

- `creator_engine`: Connects using a user with table manipulation privileges
for schema management, responsible for creating non-existing tables on app startup.
- `user_engine`: Connects using a user restricted to data operations (SELECT,
INSERT, UPDATE, DELETE).

Configuration is loaded via `EnvFile`.
"""

from sqlalchemy.ext.asyncio import create_async_engine

from envconfig import EnvFile

# Database URLs
DB_URL_USER = (
    f"mysql+asyncmy://{EnvFile.DB_USER}:{EnvFile.DB_USER_PASSWORD}@"
    f"{EnvFile.DB_HOST}:{EnvFile.DB_PORT}/{EnvFile.DB_NAME}"
)
DB_URL_CREATOR = (
    f"mysql+asyncmy://{EnvFile.DB_TABLE_CREATOR}:{EnvFile.DB_TABLE_CREATOR_PASSWORD}@"
    f"{EnvFile.DB_HOST}:{EnvFile.DB_PORT}/{EnvFile.DB_NAME}"
)

# Engine Creation
creator_engine = create_async_engine(DB_URL_CREATOR, echo=False)
user_engine = create_async_engine(DB_URL_USER, echo=False)
