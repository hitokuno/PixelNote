from fastapi import APIRouter, HTTPException
from app.schemas import CreateImageRequest, SaveDrawingRequest, RenameImageRequest
from app.models import Pixel, ImageName, Drawing
from app.db.sqlite_impl import SQLiteDB

router = APIRouter()
db = SQLiteDB()
user_id = "dummy_user"

@router.post("/api/create")
async def create_image(data: CreateImageRequest):
    image_id = await db.create_image(
        data.image_name,
        [(p.x, p.y, p.rgb) for p in data.pixels],
        user_id=user_id
    )
    return {"image_id": image_id}

@router.post("/api/save/{image_id}")
async def save_drawing(image_id: str, data: SaveDrawingRequest):
    version = await db.save_drawing(
        image_id,
        [(p.x, p.y, p.rgb) for p in data.pixels],
        user_id=user_id
    )
    return {"version": version}

@router.post("/api/rename")
async def rename_image(data: RenameImageRequest):
    await db.rename_image(data.image_id, data.new_name, user_id=user_id)
    return {"result": "ok"}

@router.get("/api/list")
async def list_images():
    rows = await db.get_image_list()
    images = [ImageName(*row) for row in rows]
    rows = await db.get_image_list()
    images = [ImageName(*row) for row in rows]
    return {"images": [i.to_dict() for i in images]}

@router.get("/api/images/{image_id}/versions")
async def get_versions(image_id: str):
    rows = await db.get_image_versions(image_id)
    drawings = [Drawing(*row) for row in rows]
    return [d.to_dict() for d in drawings]

@router.get("/api/images/{image_id}/version/{version}")
async def get_drawing(image_id: str, version: int):
    pixel_rows = await db.get_drawing_data(image_id, version)
    pixel_rows = await db.get_drawing_data(image_id, version)
    if not pixel_rows:
        raise HTTPException(status_code=404, detail="指定したバージョンの画像データがありません")
    pixels = [Pixel(*row) for row in pixel_rows]
    return {"pixels": [p.to_dict() for p in pixels]}