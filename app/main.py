from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import router
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_500_INTERNAL_SERVER_ERROR

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router)

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

