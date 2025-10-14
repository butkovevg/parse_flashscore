from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks
from pydantic import Field

from scheduler import run_mode
from src.configs.settings import settings
from src.model.response import ResponseModel, StatusModel
from src.model.types_of_sports import ModeEnum, TypesOfSportsModel, dct_rus_to_eng

router = APIRouter(
    prefix='/scheduler',
    tags=['scheduler'],
)


@router.post("/start-process/")
async def start_process(
        background_tasks: BackgroundTasks,
        rus_sport_name: TypesOfSportsModel = TypesOfSportsModel.volleyball,
        day_number: Annotated[int, Field(ge=0, le=6)] = 0,
        hidden: bool = True,
        mode: ModeEnum = ModeEnum.main,
):
    settings.IS_HEADLESS = hidden
    eng_sport_name = dct_rus_to_eng.get(rus_sport_name.value)
    background_tasks.add_task(run_mode, eng_sport_name, day_number, mode.value)
    return ResponseModel(status=StatusModel.SUCCESS,
                         data=f"Фоновая задача запущена {datetime.utcnow().isoformat() + 'Z'}")
