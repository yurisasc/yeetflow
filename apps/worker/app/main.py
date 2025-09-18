from fastapi import FastAPI

from .config import settings
from .constants import API_TITLE, API_V1_PREFIX, API_VERSION, SERVICE_NAME
from .db import init_db
from .routers import runs

app = FastAPI(
    title=API_TITLE,
    version=API_VERSION,
    debug=settings.debug,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)


@app.on_event("startup")
async def startup_event():
    """Initialize the database on startup."""
    await init_db()


app.include_router(runs.router, prefix=API_V1_PREFIX, tags=["runs"])


@app.get("/health")
async def health_check():
    """Health check endpoint for the worker service."""
    return {"status": "healthy", "service": SERVICE_NAME}
