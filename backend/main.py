"""
AI Agent Customer Service Platform - Main Entry Point
"""
import sys
import io
# Fix UTF-8 for Windows console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes import auth_routes, trip_routes, booking_routes, payment_routes, complaint_routes, refund_routes, audit_routes, dashboard_routes
from src.config import settings
from src.database import init_db
from src.utils.logger import logger

app = FastAPI(
    title="AI20K - Hiền Hựu Bus API",
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
app.include_router(auth_routes.router, prefix="/api")
app.include_router(trip_routes.router, prefix="/api")
app.include_router(booking_routes.router, prefix="/api")
app.include_router(payment_routes.router, prefix="/api")
app.include_router(complaint_routes.router, prefix="/api")
app.include_router(refund_routes.router, prefix="/api")
app.include_router(audit_routes.router, prefix="/api")
app.include_router(dashboard_routes.router, prefix="/api")


@app.on_event("startup")
async def startup_event():
    logger.info("Starting AI20K - Hiền Hựu Bus API")
    await init_db()
    logger.info("Database initialized")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down AI20K - Hiền Hựu Bus API")


@app.get("/")
async def root():
    return {
        "name": "AI20K - Hiền Hựu Bus API",
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
