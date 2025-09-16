from fastapi import FastAPI
from dotenv import load_dotenv
from .routers import runs

load_dotenv()

app = FastAPI(title="YeetFlow Worker", version="0.1.0")

app.include_router(runs.router, prefix="/api/v1", tags=["runs"])

@app.get("/health")
async def health_check():
    """Health check endpoint for the worker service."""
    return {"status": "healthy", "service": "yeetflow-worker"}
