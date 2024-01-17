from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates

from src.service.analysis import InfoAnalysisDBService
from src.service.authentication import AuthenticationService

templates = Jinja2Templates(directory="templates")
router = APIRouter(
    prefix='/analysis',
    tags=['analysis'],
)


@router.get('/get_info/')
def get_info(service: InfoAnalysisDBService = Depends()):
    """
    """
    return service.get_list_from_db()


@router.get("/matches/{day}/")
def get_value(request: Request, day: int = 0):
    matches = InfoAnalysisDBService(day).get_list_from_db()
    return templates.TemplateResponse("template.html", {"request": request, "matches": matches})


@router.get("/")
async def index(request: Request):
    matches = {"status": True}
    return templates.TemplateResponse("tabs.html", {"request": request, "matches": matches})


@router.get("/get_value")
async def get_value():
    a = 0
    if a == 1:
        service = InfoAnalysisDBService()
        return service.merge()
    else:
        return {1: 1}
