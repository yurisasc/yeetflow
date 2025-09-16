from fastapi import FastAPI
from dotenv import load_dotenv
from .routers import runs
from .constants import API_V1_PREFIX, API_TITLE, API_VERSION, SERVICE_NAME

load_dotenv()

app = FastAPI(title=API_TITLE, version=API_VERSION)

app.include_router(runs.router, prefix=API_V1_PREFIX, tags=["runs"])

@app.get("/health")
async def health_check():
    """Health check endpoint for the worker service."""
    return {"status": "healthy", "service": SERVICE_NAME}
