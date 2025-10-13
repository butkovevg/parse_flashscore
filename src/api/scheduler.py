from datetime import datetime

from fastapi import APIRouter, BackgroundTasks

from src.configs.settings import settings
from src.model.response import ResponseModel, StatusModel
from src.model.types_of_sports import ModeEnum, TypesOfSportsModel
from src.service.logger_handlers import logger

router = APIRouter(
    prefix='/scheduler',
    tags=['scheduler'],
)


# Фоновая функция
def process(sport: str, day_number: int, hidden: bool, mode: ModeEnum):
    logger.warning(f"Запущена фоновая задача: {sport=}, {day_number=}, {hidden=}, {mode=}")


@router.post("/start-process/")
async def start_process(
        background_tasks: BackgroundTasks,
        sport: TypesOfSportsModel = TypesOfSportsModel.volleyball,
        day_number: int = 0,
        hidden: bool = True,
        mode: ModeEnum = ModeEnum.current,
):
    settings.IS_HEADLESS = hidden
    background_tasks.add_task(process, sport, day_number, hidden, mode)
    return ResponseModel(status=StatusModel.SUCCESS,
                         data=f"Фоновая задача запущена {datetime.utcnow().isoformat() + 'Z'}")
