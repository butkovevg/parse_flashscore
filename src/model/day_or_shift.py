from datetime import date, datetime
from typing import Any

from fastapi import HTTPException
from pydantic import BaseModel, Field, field_validator


class DayOrShiftModel(BaseModel):
    value: int = Field(ge=-5000, le=5000)

    @field_validator('value', mode='before')
    @classmethod
    def parse_input(cls, v: Any) -> int:
        if isinstance(v, int):
            return v
        if isinstance(v, str):
            try:
                parsed_date = datetime.strptime(v, '%d.%m.%Y').date()
                return (parsed_date - date.today()).days
            except ValueError:
                try:
                    return int(v)
                except ValueError:
                    raise ValueError('Должно быть числом или датой в формате ДД.ММ.ГГГГ')  from None
        raise ValueError('Неподдерживаемый тип')  from None


async def get_day_offset(day: str) -> int:
    """Зависимость для валидации дня"""
    try:
        model = DayOrShiftModel(value=day)
        return model.value
    except Exception as e:
        raise HTTPException(status_code=400,
                            detail={
                                "error": "Неверный формат дня",
                                "message": str(e),
                                "examples": ["100", "-50", "07.02.2026"]
                            }
                            ) from None
