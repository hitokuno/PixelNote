from fastapi import APIRouter

router = APIRouter()

@router.get("/api/list")
async def list_images():
    return {"images": []}
