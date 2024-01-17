from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

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
@router.get("/test/")
async def index(request: Request):
    matches = {"status": True}
    return templates.TemplateResponse("test_html.html", {"request": request, "matches": matches})

@router.get("/get_value")
async def get_value(request: Request):
    service = InfoAnalysisDBService(-1)
    matches = service.merge()
    return templates.TemplateResponse("new_template.html", {"request": request, "matches": matches})


from fastapi.responses import FileResponse
from pathlib import Path
@router.get("/heart/")
async def get_heart():
   image_path = Path("./templates/heart.svg")
   if not image_path.is_file():
       return {"error": "Image not found on the server2"}
   return FileResponse(image_path)