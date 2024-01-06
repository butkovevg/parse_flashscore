from src.configs.settings import settings
from src.service.environment_printer import EnvironmentPrinterService

from src.service.logger_handlers import get_logger

logger = get_logger(__name__)


def main():
    exit(-1)


if __name__ == "__main__":
    logger.info(f'Initializing API {settings.TITLE}: {settings.VERSION}')
    EnvironmentPrinterService.logger_env_from_settings()
    while True:
        main()
