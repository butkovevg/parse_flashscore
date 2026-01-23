from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks
from pydantic import Field

from src.model.response import ResponseModel, StatusModel
from src.model.types_of_sports import (
    ModeParseEnum,
    TypesOfSportsModel,
)
from src.service.logger_handlers import logger
from src.service.scheduler import ManagerScheduler

router = APIRouter(
    prefix='/scheduler',
    tags=['scheduler'],
)


@router.post("/start-process/")
async def start_process(
        background_tasks: BackgroundTasks,
        rus_sport_name: TypesOfSportsModel,
        shift_day: Annotated[int, Field(ge=-1, le=6)],
        is_hidden: bool = True,
        mode_parse: ModeParseEnum = ModeParseEnum.main,
):
    logger.info(f"input for ManagerScheduler: {rus_sport_name=}, {shift_day=}, {is_hidden=}, {mode_parse=} ")
    manager_scheduler = ManagerScheduler(rus_sport_name, shift_day, is_hidden, mode_parse)
    background_tasks.add_task(manager_scheduler.run_week)
    return ResponseModel(status=StatusModel.SUCCESS,
                         data=f"Фоновая задача запущена {datetime.utcnow().isoformat() + 'Z'}")
