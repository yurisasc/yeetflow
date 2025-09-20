from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import settings
from app.constants import API_TITLE, API_V1_PREFIX, API_VERSION, SERVICE_NAME
from app.db import engine, init_db
from app.routers import artifacts, runs


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Manage application lifespan with startup and shutdown events."""
    # Startup
    await init_db()
    yield
    # Shutdown
    await engine.dispose()


app = FastAPI(
    title=API_TITLE,
    version=API_VERSION,
    debug=settings.debug,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    openapi_url="/openapi.json" if settings.debug else None,
    lifespan=lifespan,
)


app.include_router(runs.router, prefix=API_V1_PREFIX, tags=["runs"])
app.include_router(artifacts.router, prefix=API_V1_PREFIX, tags=["artifacts"])


@app.get("/health")
async def health_check():
    """Health check endpoint for the worker service."""
    return {"status": "healthy", "service": SERVICE_NAME}
