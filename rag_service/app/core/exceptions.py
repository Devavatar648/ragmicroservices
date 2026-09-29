from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

# ==========================================
# 1. Custom Exception Classes
# ==========================================
class BaseAPIException(Exception):
    """Base class for all application-specific exceptions."""
    def __init__(self, message: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class DocumentProcessingError(BaseAPIException):
    """Raised when document loading, splitting, or embedding storage fails."""
    def __init__(self, message: str = "Failed to process the uploaded document."):
        super().__init__(message=message, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)


class RAGRetrievalError(BaseAPIException):
    """Raised when vector search, BM25, or ensemble retrieval fails."""
    def __init__(self, message: str = "Error occurred while retrieving context for the query."):
        super().__init__(message=message, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AIServiceConnectionError(BaseAPIException):
    """Raised when external AI embedding or chat services are unreachable."""
    def __init__(self, message: str = "Could not communicate with the external AI service endpoint."):
        super().__init__(message=message, status_code=status.HTTP_503_SERVICE_UNAVAILABLE)


# ==========================================
# 2. Exception Handlers Registration
# ==========================================
def register_exception_handlers(app: FastAPI) -> None:
    """Registers custom exception handlers with the FastAPI application instance."""

    @app.exception_handler(BaseAPIException)
    async def custom_api_exception_handler(request: Request, exc: BaseAPIException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "status": "error",
                "error_type": exc.__class__.__name__,
                "message": exc.message,
                "path": request.url.path
            },
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        # Catch-all for unexpected Python errors (prevents server crashes and leaks)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "status": "error",
                "error_type": "InternalServerError",
                "message": "An unexpected error occurred on the server.",
                "details": str(exc),
                "path": request.url.path
            },
        )