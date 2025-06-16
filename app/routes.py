from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Tuple
from app.db.sqlite_impl import SQLiteDB

db = SQLiteDB()
router = APIRouter()

class CreateImageRequest(BaseModel):
    image_name: str
    pixels: List[Tuple[int, int, str]]

class SaveDrawingRequest(BaseModel):
    image_id: str
    pixels: List[Tuple[int, int, str]]

class RenameImageRequest(BaseModel):
    image_id: str
    new_name: str

@router.post("/api/create")
async def create_image(req: CreateImageRequest):
    return {"image_id": await db.create_image(req.image_name, req.pixels, "dummy_user")}

@router.post("/api/save")
async def save_drawing(req: SaveDrawingRequest):
    return {"version": await db.save_drawing(req.image_id, req.pixels, "dummy_user")}

@router.post("/api/rename")
async def rename_image(req: RenameImageRequest):
    await db.rename_image(req.image_id, req.new_name, "dummy_user")
    return {"status": "ok"}

@router.get("/api/list")
async def get_list():
    return await db.get_image_list()

@router.get("/api/images/{image_id}/versions")
async def get_versions(image_id: str):
    return await db.get_image_versions(image_id)

@router.get("/api/images/{image_id}/{version}")
async def get_drawing(image_id: str, version: int):
    data = await db.get_drawing_data(image_id, version)
    if data is None:
        raise HTTPException(status_code=404, detail="Version not found")
    return {"pixels": data}
