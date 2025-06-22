from pydantic import BaseModel, Field, validator
from fastapi.exceptions import RequestValidationError
import re

class Pixel(BaseModel):
    x: int
    y: int
    rgb: str

    @validator('rgb')
    def rgb_format(cls, v):
        if not re.fullmatch(r'^#[0-9A-Fa-f]{6}$', v):
            raise RequestValidationError([{
                "loc": ("body", "rgb"),
                "msg": "#RRGGBB形式で指定してください",
                "type": "value_error.wrong_format",
                "input": v
            }])
        return v

class CreateImageRequest(BaseModel):
    image_name: str
    pixels: list[Pixel]

    @validator('image_name')
    def image_name_len(cls, v):
        if len(v) > 255:
            raise RequestValidationError([{
                "loc": ("body", "image_name"),
                "msg": "255文字以内で指定してください",
                "type": "value_error.too_long",
                "input": v
            }])
        return v

class RenameImageRequest(BaseModel):
    image_id: str
    new_name: str

    @validator('image_id')
    def image_id_len(cls, v):
        if len(v) > 36:
            raise RequestValidationError([{
                "loc": ("body", "image_id"),
                "msg": "36文字以内で指定してください",
                "type": "value_error.too_long",
                "input": v
            }])
        return v

    @validator('new_name')
    def new_name_len(cls, v):
        if len(v) > 255:
            raise RequestValidationError([{
                "loc": ("body", "new_name"),
                "msg": "255文字以内で指定してください",
                "type": "value_error.too_long",
                "input": v
            }])
        return v
