from datetime import datetime
from enum import Enum

from fastapi import APIRouter, BackgroundTasks

from src.model.response import ResponseModel, StatusModel
from src.service.logger_handlers import logger


class ModeEnum(str, Enum):
    main = "main"
    current = "current"


# Фоновая функция
def process(sport: str, day_number: int, hidden: bool, mode: ModeEnum):
    logger.info(f"Запущена фоновая задача: {sport=}, {day_number=}, {hidden=}, {mode=}")


router = APIRouter(
    prefix='/scheduler',
    tags=['scheduler'],
)


@router.post("/start-process/")
async def start_process(
        background_tasks: BackgroundTasks,
        sport: str,
        day_number: int,
        hidden: bool,
        mode: ModeEnum
):

    background_tasks.add_task(process, sport, day_number, hidden, mode)
    return ResponseModel(status=StatusModel.SUCCESS,
                         data=f"Фоновая задача запущена {datetime.utcnow().isoformat() + 'Z'}")
