import uvicorn

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.api.v1.routes import router
from app.core.exceptions import UserNotFoundException, ExceptionHandler

app = FastAPI(
    title = settings.APP_TITLE,
    version = settings.APP_VERSION,
)



app.include_router(router, prefix='/api/v1')

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(UserNotFoundException)
async def todo_not_found_handler(
        request: Request,
        exc: UserNotFoundException
):
    return JSONResponse(
        status_code=404,
        content={
            "message": str(exc)
        }
    )

@app.exception_handler(ExceptionHandler)
async def todo_exception_handler(
        request: Request,
        exc: ExceptionHandler
):
    return JSONResponse(
        status_code=400,
        content={
            "message": str(exc)
        }
    )

if __name__ == '__main__':
    uvicorn.run('main:app', port=int(settings.APP_PORT), reload=True)
