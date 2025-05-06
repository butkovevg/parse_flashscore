import os

from pydantic_settings import BaseSettings

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
PATH_ENV = os.path.join(ROOT_DIR, '.env')


class Setting(BaseSettings):
    """Класс работы с .env"""
    TITLE: str = "parse_flashscore"
    DESCRIPTION: str = ""
    VERSION: str = "v0.0.5"
    NAME: str = ""
    EMAIL: str = "butkovevg@yandex.ru"
    MSG_ERROR: str = f"please, contact the developer {EMAIL}"

    # уровень логирования CRITICAL(50)-ERROR(40)-WARNING(30)-INFO(20)-DEBUG(10)-NOTSET(0)
    LEVEL_LOGGER_HANDLER: int = 10

    # DB
    DRIVER_NAME: str
    DB_HOST: str
    DB_PORT: int
    DB_USERNAME: str
    DB_PASSWORD: str
    DB_NAME: str
    SCHEME_NAME: str
    TABLE_NAME_MAIN: str = "main"
    TABLE_NAME_CURRENT: str = "current"
    TABLE_NAME_ANALYSIS: str = "analysis"
    DB_ECHO: bool = True  # logging database

    @property
    def DB_URL(self):
        """DSN MAIN DB"""
        return f"{self.DRIVER_NAME}://{self.DB_USERNAME}:{self.DB_PASSWORD}@" \
               f"{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def DATABASE_URL_ASYNCPG(self):
        """ToDo: вынести DRIVER_NAME"""
        # DSN postgresql+asyncpg://postgres:postgres@localhost:5432/sa
        return f"postgresql+asyncpg://{self.DB_USERNAME}:{self.DB_PASSWORD}@" \
               f"{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def DATABASE_URL_PSYCOPG(self):
        """ToDo: вынести DRIVER_NAME"""
        # DSN postgresql+psycopg://postgres:postgres@localhost:5432/sa
        return f"postgresql+psycopg://{self.DB_USERNAME}:{self.DB_PASSWORD}@" \
               f"{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    SERVER_HOST: str = ""
    SERVER_PORT: int

    PAUSE_SEC: int = 10

    class Config:
        env_file = PATH_ENV
        env_file_encoding = 'utf-8'


settings = Setting()
