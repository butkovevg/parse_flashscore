from fastapi import APIRouter, Depends
from fastapi import  Request
from fastapi.templating import Jinja2Templates
from src.service.analysis import InfoAnalysisDBService

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
def get_value( request: Request, day: int=0):
    matches = InfoAnalysisDBService(day).get_list_from_db()
    return templates.TemplateResponse("template.html", {"request": request, "matches": matches})
from src.service.logger_handlers import get_logger


logger = get_logger(__name__)
@router.get("/")
async def index(request: Request):
    matches = {"status": "success"}
    return templates.TemplateResponse("tabs.html", {"request": request, "matches": matches})
from fastapi.responses import JSONResponse
@router.get("/get_value")
async def get_value():
   # Here you would call your get_value() function
   # For demonstration purposes, we'll just simulate a delay
   import time
   time.sleep(1)
   return JSONResponse(content={"status": "success"})