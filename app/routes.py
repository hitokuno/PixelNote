from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from typing import List, Tuple
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_500_INTERNAL_SERVER_ERROR
import traceback
from app.db.sqlite_impl import SQLiteDB
from app.routes import router

db = SQLiteDB()
app = FastAPI()
app.include_router(router)

class CreateImageRequest(BaseModel):
    image_name: str
    pixels: List[Tuple[int, int, str]]

class SaveDrawingRequest(BaseModel):
    image_id: str
    pixels: List[Tuple[int, int, str]]

class RenameImageRequest(BaseModel):
    image_id: str
    new_name: str

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for err in exc.errors():
        field = ".".join(str(l) for l in err["loc"][1:])  # "body.image_name"など→"image_name"
        value = exc.body if isinstance(exc.body, dict) and field in exc.body else None
        if value is None and isinstance(exc.body, dict):
            value = exc.body.get(field.split(".")[0], None)
        errors.append({
            "field": field,
            "value": value,
            "message": err["msg"]
        })
    return JSONResponse(
        status_code=HTTP_400_BAD_REQUEST,
        content={"errors": errors}
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": str(exc)}
    )

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
    return await db.get_image_list()  # 画像リストのみ返却

@router.get("/api/images/{image_id}/versions")
async def get_versions(image_id: str):
    return await db.get_image_versions(image_id)

@router.get("/api/images/{image_id}/{version}")
async def get_drawing(image_id: str, version: int):
    data = await db.get_drawing_data(image_id, version)
    if data is None:
        raise HTTPException(status_code=404, detail="Version not found")
    return {"pixels": data}
