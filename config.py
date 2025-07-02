from pydantic_settings import BaseSettings


class Env(BaseSettings):
    db_user: str
    db_password: str

    class Config:
        env_file = ".env"


Env = Env()
