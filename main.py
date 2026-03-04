import logging
import multiprocessing
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from prometheus_fastapi_instrumentator import Instrumentator

from src.api import router
from src.configs.settings import settings
from src.model.custom_exception import CustomExceptionModel
from src.service.custom_handler_exception import CustomException
from src.service.environment_printer import EnvironmentPrinterService
from src.service.logger_handlers import get_logger

logger = get_logger(__name__)
tags_metadata = [
    {'name': 'analysis',
     'description':
         """
         Описание:\n
         Появится позже\n
         """
     },
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f'Initializing API {settings.TITLE}: {settings.VERSION}')
    logger.info(f'Visit endpoint: http://{settings.SERVER_HOST}:{settings.SERVER_PORT}/analysis/time/0/')
    if settings.LEVEL_LOGGER_HANDLER == logging.DEBUG:
        EnvironmentPrinterService.logger_env_from_settings()
        EnvironmentPrinterService.logger_all_environment_variables()
    yield
    logger.info(f'Shutting down API {settings.TITLE}: {settings.VERSION}')


app = FastAPI(
    title=settings.TITLE,
    description=settings.DESCRIPTION,
    version=settings.VERSION,
    contact={
        "name": settings.NAME,
        "email": settings.EMAIL
    },
    license_info={},
    openapi_tags=tags_metadata,
    lifespan=lifespan,
)

Instrumentator().instrument(app).expose(app, endpoint="/metrics")

# Добавление middleware (важно: до регистрации маршрутов)
# app.add_middleware(LoggingMiddleware)

app.mount("/static", StaticFiles(directory="templates"), name="static")
app.include_router(router)


# Обработчик пользовательских исключений, который "ловит" все необработанные исключения
@app.exception_handler(CustomException)
async def get_custom_exception(request: Request, exc: CustomException):
    logger.error(f"custom_exception {exc.status_code}: {exc.detail}")
    error = jsonable_encoder(
        CustomExceptionModel(status_code=exc.status_code, er_message=exc.message, er_details=exc.detail))
    return JSONResponse(status_code=exc.status_code, content=error)


# Обработчик глобальных исключений, который "ловит" все необработанные исключения
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    if settings.LEVEL_LOGGER_HANDLER == logging.DEBUG:  # DEBUG
        description_error = str(exc)

    else:
        description_error = "Internal server error"
    logger.warning("Traceback:", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": description_error}
    )


if __name__ == '__main__':
    multiprocessing.freeze_support()
    # uvicorn file:instance_API --reload
    uvicorn.run(
        'main:app',
        host=settings.SERVER_HOST,
        port=settings.SERVER_PORT,
        reload=True,
        log_level="info",  # или "warning", "error"
        access_log=False  # ← вот это отключает логи запросов
    )
