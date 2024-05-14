from fastapi import APIRouter
from fastapi.responses import FileResponse

router = APIRouter(prefix="/favicon.ico")

favicon_path = "./static/images/favicon/ball.ico"

@router.get("", include_in_schema=False)
def favicon():
    return FileResponse(favicon_path)
# import os
# favicon_path = os.path.join(os.path.dirname(__file__), "static", "images", "favicon", "ball.ico")
# print(favicon_path)