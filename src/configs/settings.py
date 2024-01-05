from typing import List, Union

from pydantic_settings import BaseSettings

PATH_ENV = "/srv/dq/etc/.env_executor"


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


    class Config:
        env_file = PATH_ENV
        env_file_encoding = 'utf-8'


settings = Setting()
