import time

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from src.service.logger_handlers import logger


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Лог до запроса
        start_time = time.time()
        logger.info(f"→ Incoming request: {request.method} {request.url}")

        # Выполняем обработку запроса
        try:
            response: Response = await call_next(request)
        except Exception as e:
            # Логируем ошибку и пробрасываем исключение
            logger.error(f"→ Request failed with error: {e}")
            raise

        # Лог после запроса
        process_time = time.time() - start_time
        logger.info(
            f"← Outgoing response: {request.method} {request.url} "
            f"Status: {response.status_code} | "
            f"Duration: {process_time:.3f}s"
        )
