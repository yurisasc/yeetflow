from dotenv import load_dotenv
from fastapi import FastAPI

from .constants import API_TITLE, API_V1_PREFIX, API_VERSION, SERVICE_NAME
from .routers import runs

load_dotenv()

app = FastAPI(title=API_TITLE, version=API_VERSION)

app.include_router(runs.router, prefix=API_V1_PREFIX, tags=["runs"])


@app.get("/health")
async def health_check():
    """Health check endpoint for the worker service."""
    return {"status": "healthy", "service": SERVICE_NAME}
