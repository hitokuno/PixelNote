from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Tuple
from app.db import get_db
from app.errors import ErrorCode

router = APIRouter()

class CreateRequest(BaseModel):
    image_name: str
    pixels: List[Tuple[int, int, str]]

class UpdateRequest(BaseModel):
    image_id: str
    image_name: str
    pixels: List[Tuple[int, int, str]]

class RenameRequest(BaseModel):
    image_id: str
    new_name: str

@router.get("/list")
async def list_images(db=Depends(get_db)):
    return await db.get_image_list()

@router.get("/images/{image_id}/versions")
async def get_versions(image_id: str, db=Depends(get_db)):
    versions = await db.get_image_versions(image_id)
    if not versions:
        raise HTTPException(status_code=404, detail=ErrorCode.IMAGE_NOT_FOUND)
    return {"versions": versions}

@router.get("/images/{image_id}/{version}")
async def get_drawing(image_id: str, version: int, db=Depends(get_db)):
    pixels = await db.get_drawing_data(image_id, version)
    if pixels is None:
        raise HTTPException(status_code=404, detail=ErrorCode.VERSION_NOT_FOUND)
    return {"pixels": pixels}

@router.post("/create")
async def create_image(req: CreateRequest, db=Depends(get_db), user_id: str = Depends(lambda: "test_user")):
    image_id = await db.create_image(req.image_name, req.pixels, user_id)
    return {"image_id": image_id}

@router.post("/update")
async def update_image(req: UpdateRequest, db=Depends(get_db), user_id: str = Depends(lambda: "test_user")):
    version = await db.save_drawing(req.image_id, req.pixels, user_id)
    return {"version": version}

@router.post("/rename")
async def rename_image(req: RenameRequest, db=Depends(get_db), user_id: str = Depends(lambda: "test_user")):
    await db.rename_image(req.image_id, req.new_name, user_id)
    return {"message": "updated"}
