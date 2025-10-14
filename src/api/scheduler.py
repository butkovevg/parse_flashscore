from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks
from pydantic import Field

from src.configs.settings import settings
from src.model.response import ResponseModel, StatusModel
from src.model.types_of_sports import (
    ModeEnum,
    TypesOfSportsModel,
    dct_rus_to_eng,
)
from src.service.scheduler import SchedulerService, get_scheduler_service, run_mode

router = APIRouter(
    prefix='/scheduler',
    tags=['scheduler'],
)


@router.post("/start-process/")
async def start_process(
        background_tasks: BackgroundTasks,
        rus_sport_name: TypesOfSportsModel = TypesOfSportsModel.volleyball,
        shift_day: Annotated[int, Field(ge=0, le=6)] = 0,
        hidden: bool = True,
        mode: ModeEnum = ModeEnum.main,
):
    settings.IS_HEADLESS = hidden
    eng_sport_name = dct_rus_to_eng.get(rus_sport_name.value)
    scheduler_service: SchedulerService = get_scheduler_service(eng_sport_name=eng_sport_name, shift_day=shift_day)
    background_tasks.add_task(run_mode, scheduler_service, mode.value)
    return ResponseModel(status=StatusModel.SUCCESS,
                         data=f"Фоновая задача запущена {datetime.utcnow().isoformat() + 'Z'}")
