from fastapi import APIRouter, Depends
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from src.service.analysis import InfoAnalysisDBService

router = APIRouter(
    prefix='/analysis',
    tags=['analysis'],
)


@router.get('/get_info/')
def get_info(service: InfoAnalysisDBService = Depends()):
    """
    """
    return service.get_list_from_db()


@router.get("/get_value/{id}/")
def get_value(id):
    return {"id": id}


templates = Jinja2Templates(directory="templates")


@router.get("/matches/")
def read_matches(request: Request):
    matches = InfoAnalysisDBService().get_list_from_db()

    return templates.TemplateResponse("template.html", {"request": request, "matches": matches})

@router.get("/")
def index(request: Request):
    matches = {}

    return templates.TemplateResponse("template1.html", {"request": request, "matches": matches})