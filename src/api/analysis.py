from datetime import datetime

from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates
from starlette.background import BackgroundTasks

from src.model.day_or_shift import get_day_offset
from src.service.analysis import InfoAnalysisDBService
from src.service.background_tasks import run
from src.service.find_day_for_parsing import FindDayForParsingService
from src.service.online import DataBaseOnlineService

templates = Jinja2Templates(directory="templates")

router = APIRouter(
    prefix='/analysis',
    tags=['analysis'],
)


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


# @router.get("/time/{day}/")
# async def get_time_value(request: Request, day: int):
#     service = InfoAnalysisDBService(day)
#     matches = service.get_match_today()
#     return templates.TemplateResponse("analysis_time.html", {"request": request, "matches": matches, "day": day})


@router.get("/time/{day}/")
async def get_time_value(
        request: Request,
        day: int = Depends(get_day_offset)
):
    service = InfoAnalysisDBService(day)
    matches = service.get_match_today()

    return templates.TemplateResponse(
        "analysis_time.html",
        {"request": request, "matches": matches, "day": day}
    )

@router.get("/render/")
async def test_render(request: Request):
    return templates.TemplateResponse("test_render.html", {"request": request, "who_now_win": None, "who_must_win": 0})


@router.get("/time/{day}/json")
async def get_time_value_json(request: Request, day: int):
    service = InfoAnalysisDBService(day)
    matches = service.get_match_today()
    return matches


@router.get("/{day}/")
async def get_value(request: Request, day: int = 0):
    service = InfoAnalysisDBService(day)
    matches = service.merge()
    return templates.TemplateResponse("analysis.html", {"request": request, "matches": matches, "day": day})


@router.get("/find_day")
async def find_day(request: Request):
    service = FindDayForParsingService()
    data = service.all()
    return templates.TemplateResponse("find.html", {"request": request,
                                                    "data": data,
                                                    "sports": list(
                                                        FindDayForParsingService.dct_types_of_sports.keys())})


@router.get("/for_stat")
async def for_stat(request: Request):
    service = FindDayForParsingService()
    data = service.all()
    data_for_stat = service.for_stat(data)
    return templates.TemplateResponse("for_stat.html", {"request": request,
                                                        "data": data,
                                                        "sports": list(
                                                            FindDayForParsingService.dct_types_of_sports.keys()),
                                                        "data_for_stat": data_for_stat})


@router.patch("/update_comment/{link}")
async def update_comment(request: Request, link: str, comment: str | None = None):
    comment = f"{comment} {str(datetime.now())}"
    database_online_service = DataBaseOnlineService()
    database_online_service.update_comment(link, comment)
    return {"message": "Comment updated successfully", "link": link, "new_comment": comment}


@router.patch("/get_historical_analytics/{match_date}/")
async def get_historical_analytics(request: Request, match_date: str):
    database_online_service = DataBaseOnlineService()
    return database_online_service.get_historical_analytics(match_date=match_date)
