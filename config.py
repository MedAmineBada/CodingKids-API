from pydantic_settings import BaseSettings


class Env(BaseSettings):
    db_host: str
    db_port: int
    db_user: str
    db_password: str
    db_name: str

    class Config:
        env_file = ".env"


Env = Env()
