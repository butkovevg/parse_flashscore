from enum import Enum
from typing import Any

from pydantic import BaseModel


class StatusModel(str, Enum):
    ERROR = "error"
    SUCCESS = "success"


class ResponseModel(BaseModel):
    """Для стандартных ответов"""
    status: StatusModel = StatusModel.SUCCESS
    data: Any = None
    details: Any = None
