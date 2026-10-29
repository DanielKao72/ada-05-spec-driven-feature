from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.exceptions import StorageCorruptedError
from app.routers.customer_router import router as customer_router


def create_app() -> FastAPI:
    """Application factory initializing FastAPI with routes and metadata."""
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="RESTful API for searching and managing customer records using local JSON persistence.",
    )

    app.include_router(customer_router)

    @app.exception_handler(StorageCorruptedError)
    def storage_corrupted_handler(request: Request, exc: StorageCorruptedError) -> JSONResponse:
        # Details are logged by the repository; the client gets a generic message.
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error."},
        )

    @app.get("/health", tags=["Health"])
    def health_check() -> dict[str, str]:
        return {"status": "healthy", "version": settings.app_version}

    return app


app = create_app()
