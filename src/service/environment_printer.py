import os

from src.configs.settings import settings
from src.service.logger_handlers import get_logger

logger = get_logger(__name__)


class EnvironmentPrinterService:
    DIVIDING_LINE = "_" * 88

    @classmethod
    def logger_env_from_settings(cls):
        logger.debug(cls.DIVIDING_LINE)
        settings_dict = settings.dict()
        for key in settings_dict:
            logger.debug(f"env_from_settings {key}: {settings_dict[key]}")
        logger.debug(cls.DIVIDING_LINE)

    @classmethod
    def logger_all_environment_variables(cls):
        logger.debug(cls.DIVIDING_LINE)
        for key, value in os.environ.items():
            logger.debug(f"all_environment_variables {key}: {value}")
        logger.debug(cls.DIVIDING_LINE)
