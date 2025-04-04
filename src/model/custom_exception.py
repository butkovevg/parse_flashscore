from pydantic import BaseModel, Field,  FieldValidationInfo, field_validator

# Pydantic модель ответов на ошибки
class CustomExceptionModel(BaseModel):
    status_code: int 
    er_message: str 
    er_details: str


class ItemsResponse(BaseModel):
    item_id: float = Field(..., gt=0)  #  должен быть больше 0

    @field_validator("item_id")
    @classmethod
    def validate_price(cls, value: float, info: FieldValidationInfo):
        if value < 0:
            raise ValueError("Price must be non-negative")
        return value

# По умолчанию Pydantic(ValidationError)->RequestValidationError
# {
#   "detail": [
#     {
#       "loc": ["body", "price"],
#       "msg": "ensure this value is greater than 0",
#       "type": "value_error.number.gt"
#     }
#   ]
# }