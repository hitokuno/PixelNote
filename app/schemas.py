from pydantic import BaseModel, validator
import re

class PixelSchema(BaseModel):
    x: int
    y: int
    rgb: str

    @validator('rgb')
    def rgb_format(cls, v):
        if len(v) > 7:
            raise ValueError('rgbは7文字以内で指定してください')
        if not re.fullmatch(r'#[0-9A-Fa-f]{6}', v):
            raise ValueError('rgbは#RRGGBB形式で指定してください')
        return v

class CreateImageRequest(BaseModel):
    image_name: str
    pixels: list[PixelSchema]

    @validator('image_name')
    def image_name_len(cls, v):
        if len(v) > 255:
            raise ValueError('image_nameは255文字以内で指定してください')
        return v

class SaveDrawingRequest(BaseModel):
    pixels: list[PixelSchema]

class RenameImageRequest(BaseModel):
    image_id: str
    new_name: str

    @validator('image_id')
    def image_id_len(cls, v):
        if len(v) > 36:
            raise ValueError('image_idは36文字以内で指定してください')
        return v

    @validator('new_name')
    def new_name_len(cls, v):
        if len(v) > 255:
            raise ValueError('new_nameは255文字以内で指定してください')
        return v
