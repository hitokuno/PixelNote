from pydantic import BaseModel, Field, validator
import re

class Pixel(BaseModel):
    x: int
    y: int
    rgb: str = Field(..., max_length=7)

    @validator('rgb')
    def rgb_format(cls, v):
        if not re.fullmatch(r'#[0-9A-Fa-f]{6}', v):
            raise ValueError('rgb must be hex format like "#FF00AA"')
        return v

class CreateImageRequest(BaseModel):
    image_name: str = Field(..., max_length=255)
    pixels: list[Pixel]

class SaveDrawingRequest(BaseModel):
    pixels: list[Pixel]

class RenameImageRequest(BaseModel):
    image_id: str = Field(..., max_length=36)
    new_name: str = Field(..., max_length=255)
