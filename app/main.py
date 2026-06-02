from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from app.database.base import Base
from app.database.session import engine
from app.routes import analysis, etl, measurements


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create database tables on application startup.

    For larger production systems, replace this with Alembic migrations.
    """
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Industrial Data API",
    description="Backend service for storing, processing, and analyzing industrial machine process data.",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(measurements.router)
app.include_router(etl.router)
app.include_router(analysis.router)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Validation error",
            "detail": exc.errors(),
        },
    )


@app.exception_handler(SQLAlchemyError)
async def database_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Database error",
            "detail": "The request could not be completed. Please try again later.",
        },
    )


@app.get("/health", tags=["Health"])
def health_check() -> dict[str, str]:
    """Health check endpoint for containers and monitoring."""
    return {"status": "ok"}