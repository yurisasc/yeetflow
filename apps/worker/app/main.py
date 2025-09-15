from fastapi import FastAPI

app = FastAPI(title="YeetFlow Worker", version="0.1.0")

@app.get("/health")
async def health_check():
    """Health check endpoint for the worker service."""
    return {"status": "healthy", "service": "yeetflow-worker"}
