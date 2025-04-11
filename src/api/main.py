from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from src.configs.settings import settings
router = APIRouter()

# Настройка Jinja2Templates
templates = Jinja2Templates(directory="templates")


# # Примеры endpoint'ов
# @router.get("/home")
# async def home():
#     return {"message": "Welcome to the home page!"}
#
#
# @router.get("/about")
# async def about():
#     return {"message": "About page"}
#
#
# @router.get("/contact")
# async def contact():
#     return {"message": "Contact us"}


# Главная страница, которая отображает все endpoint'ы
@router.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    # # Получаем все маршруты из app.routes
    # routes = [
    #     {"path": route.path, "methods": route.methods}
    #     for route in router.routes
    #     if hasattr(route, "path")  # Фильтруем только маршруты с атрибутом path
    # ]
    routes = [

        {
            "path": "",
            "methods": "",
            "url": f"http://{settings.SERVER_HOST}:{settings.SERVER_PORT}/analysis/find_day",
        },
        {
            "path": "",
            "methods": "",
            "url": f"http://{settings.SERVER_HOST}:{settings.SERVER_PORT}/analysis/time/0/",
        },
        {
            "path": "",
            "methods": "",
            "url": f"http://{settings.SERVER_HOST}:{settings.SERVER_PORT}/analysis/0/",
        }

    ]

    return templates.TemplateResponse(
        "index.html", {"request": request, "routes": routes}
    )
