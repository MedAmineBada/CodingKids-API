from pydantic_settings import BaseSettings


class EnvFile(BaseSettings):
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str

    DB_USER: str
    DB_USER_PASSWORD: str

    DB_TABLE_CREATOR: str
    DB_TABLE_CREATOR_PASSWORD: str

    class Config:
        env_file = ".env"


EnvFile = EnvFile()
