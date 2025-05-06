from fastapi import APIRouter, status

from src.model.custom_exception import CustomExceptionModel, ItemsResponse
from src.service.custom_handler_exception import CustomException

router = APIRouter(
    prefix='/exc',
    tags=['exc'],
)


# ДОБАВИЛИ много мета-информации для описания нашей конечной точки
@router.get(
    "/items/{item_id}/",
    response_model=ItemsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Items by ID.",
    description="The endpoint returns item_id by ID. If the item_id is 42, an exception with the status code 404 is returned.",
    responses={
        status.HTTP_200_OK: {'model': ItemsResponse},
        status.HTTP_404_NOT_FOUND: {'model': CustomExceptionModel},  # вот тут применяем схемы ошибок пидантика
    },
)
async def read_item(item_id: int):
    my_id = 0
    if item_id == my_id:
        raise CustomException(detail="Item not found", status_code=404,
                              message="You're trying to get an item that doesn't exist. Try entering a different item_id.")
    return {"item_id": item_id}
