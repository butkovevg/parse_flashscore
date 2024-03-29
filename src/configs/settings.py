import os

from pydantic_settings import BaseSettings

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
PATH_ENV = os.path.join(ROOT_DIR, '.env')


class Setting(BaseSettings):
    """Класс работы с .env"""
    #  Блок, который универсальный (не должен быть в .env)
    TITLE: str = "parse_flashscore"
    DESCRIPTION: str = ""
    VERSION: str = "v0.0.1"
    NAME: str = ""
    EMAIL: str = ""
    MSG_ERROR: str = f"please, contact the developer {EMAIL}"

    # для логирования
    # уровни CRITICAL(50)-ERROR(40)-WARNING(30)-INFO(20)-DEBUG(10)-NOTSET(0)
    LEVEL_LOGGER_HANDLER: int = 10

    # DB
    DRIVER_NAME: str = ""
    HOST_DB: str = ""
    PORT_DB: int = 0
    USERNAME_DB: str = ""
    PASSWORD_DB: str = ""
    DB_NAME: str = ""
    SCHEME_NAME: str = ""
    TABLE_NAME_MAIN: str = "main"
    TABLE_NAME_CURRENT: str = "current"

    SERVER_HOST: str = ""
    SERVER_PORT: int

    class Config:
        env_file = PATH_ENV
        env_file_encoding = 'utf-8'


settings = Setting()
