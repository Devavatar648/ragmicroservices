from fastapi import FastAPI

from app.config import settings
from app.api.v1.routes import router
from app.core.exceptions import register_exception_handlers

app = FastAPI(
    title = settings.APP_TITLE,
    version = settings.APP_VERSION,
)

app.include_router(router)
register_exception_handlers(app)
