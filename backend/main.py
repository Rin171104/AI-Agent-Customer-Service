"""
AI Agent Customer Service Platform - Main Entry Point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes import router as api_router
from src.utils.config import settings
from src.utils.logger import logger

app = FastAPI(
    title="AI Agent Customer Service API",
    description="Multi-Agent AI System for Bus Ticket Booking & Customer Service",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api")


@app.on_event("startup")
async def startup_event():
    logger.info("Starting AI Agent Customer Service API")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down AI Agent Customer Service API")


@app.get("/")
async def root():
    return {
        "name": "AI Agent Customer Service API",
        "version": "1.0.0",
        "status": "running",
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
