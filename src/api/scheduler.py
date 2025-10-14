from datetime import datetime

from fastapi import APIRouter, BackgroundTasks

from scheduler import run_scheduler
from src.configs.settings import settings
from src.model.response import ResponseModel, StatusModel
from src.model.types_of_sports import ModeEnum, TypesOfSportsModel

router = APIRouter(
    prefix='/scheduler',
    tags=['scheduler'],
)


@router.post("/start-process/")
async def start_process(
        background_tasks: BackgroundTasks,
        sport_name: TypesOfSportsModel = TypesOfSportsModel.volleyball,
        day_number: int = 0,
        hidden: bool = True,
        mode: ModeEnum = ModeEnum.current,
):
    settings.IS_HEADLESS = hidden
    background_tasks.add_task(run_scheduler, sport_name.value, day_number, mode.value)
    return ResponseModel(status=StatusModel.SUCCESS,
                         data=f"Фоновая задача запущена {datetime.utcnow().isoformat() + 'Z'}")
