from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates


from src.service.analysis import InfoAnalysisDBService


templates = Jinja2Templates(directory="templates")

router = APIRouter(
    prefix='/favorites',
    tags=['favorites'],
)

@router.get("/{day}/")
async def get_favorites(request: Request, day: int = 0):
    service = InfoAnalysisDBService(day)
    matches = service.get_favorites()
    return templates.TemplateResponse("favorites.html", {"request": request, "matches": matches, "day": day})
