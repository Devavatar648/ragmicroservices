import uvicorn

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.config import settings
from app.api.v1.routes import router
from app.core.exceptions import ExceptionHandler

app = FastAPI(
    title = settings.APP_TITLE,
    version = settings.APP_VERSION,
)

app.include_router(router, prefix='/api/v1')

@app.exception_handler(ExceptionHandler)
async def ai_exception_handler(
        request: Request,
        exc: ExceptionHandler
):
    return JSONResponse(
        status_code=400,
        content={
            "message": str(exc)
        }
    )

