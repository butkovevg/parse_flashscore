#!/usr/bin/python3
# -*- coding: utf-8 -*-

import multiprocessing
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from src.api import router
from src.configs.settings import settings
from src.service.custom_handler_exception import MyCustomException
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
    # EnvironmentPrinterService.logger_env_from_settings()
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
app.mount("/static", StaticFiles(directory="templates"), name="static")
app.include_router(router)


@app.exception_handler(MyCustomException)
async def get_my_custom_exception(request: Request, exception: MyCustomException):
    return JSONResponse(status_code=exception.status_code, content={
        "status": exception.status,
        "data": exception.data,
        "details": exception.details
    })


if __name__ == '__main__':
    multiprocessing.freeze_support()
    # uvicorn file:instance_API --reload
    uvicorn.run(
        'main:app',
        host=settings.SERVER_HOST,
        port=settings.SERVER_PORT,
        reload=True,
    )
