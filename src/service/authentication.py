from src.service.logger_handlers import get_logger

logger = get_logger(__name__)


class AuthenticationService:

    def __init__(self):
        self.a = 1
        logger.warning(f"{self.a=}")

    def get(self):
        logger.warning(f"{self.a=}")
        return {1: 1}
