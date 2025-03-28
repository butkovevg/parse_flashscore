from datetime import datetime

from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from starlette.background import BackgroundTasks

from src.service.analysis import InfoAnalysisDBService
from src.service.find_day_for_parsing import FindDayForParsingService
from src.service.tennis import TennisService

templates = Jinja2Templates(directory="templates")

router = APIRouter(
    prefix='/tennis',
    tags=['tennis'],
)

from src.service.background_tasks import run









@router.get("/{day}/")
def get_tennis_match_for_day(day: int = 0):
    service = TennisService(day)
    # matches = service.merge()
    # return templates.TemplateResponse("analysis.html", {"request": request, "matches": matches, "day": day})
    return service.main()
