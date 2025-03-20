from datetime import datetime

from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from starlette.background import BackgroundTasks

from src.service.analysis import InfoAnalysisDBService
from src.service.find_day_for_parsing import FindDayForParsingService

templates = Jinja2Templates(directory="templates")

router = APIRouter(
    prefix='/analysis',
    tags=['analysis'],
)

from src.service.background_tasks import run


@router.get("/test_fone/")
async def test_fone(background_tasks: BackgroundTasks):
    background_tasks.add_task(run, 11)
    current_time = datetime.now()
    time_filter = current_time.strftime('%H:%M:%S')
    matches = {
        "id": 123,
        "status": False,
        "dt": str(time_filter),

    }
    return matches


@router.get("/test/")
async def test(request: Request):
    current_time = datetime.now()
    time_filter = current_time.strftime('%H:%M:%S')
    matches = {
        "id": 123,
        "status": False,
        "dt": str(time_filter),

    }
    return templates.TemplateResponse("test_html.html", {"request": request, "matches": matches})


@router.get("/update_favorites/{analysis_id}")
async def update_favorites(analysis_id: int):
    parsing_service = InfoAnalysisDBService()
    return parsing_service.update_favorites(analysis_id=analysis_id)


@router.get("/time/{day}/")
async def get_value(request: Request, day: int):
    service = InfoAnalysisDBService(day)
    matches = service.get_match_today()
    return templates.TemplateResponse("analysis.html", {"request": request, "matches": matches, "day": day})


@router.get("/{day}/")
async def get_value(request: Request, day: int = 0):
    service = InfoAnalysisDBService(day)
    matches = service.merge()
    return templates.TemplateResponse("analysis.html", {"request": request, "matches": matches, "day": day})


@router.get("/find_day")
async def find_day(request: Request):
    service = FindDayForParsingService()
    data = service.all()
    list_sports = ['ВОЛЕЙБОЛ', 'ФУТБОЛ', 'БАСКЕТБОЛ', 'ГАНДБОЛ', 'ТЕННИС']

    return templates.TemplateResponse("find.html", {"request": request,
                                                    "data": data,
                                                    "sports": list_sports})

