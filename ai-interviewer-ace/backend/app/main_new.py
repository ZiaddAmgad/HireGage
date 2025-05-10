"""
Main application entry point for the HireGage AI Interview Agent.
This module initializes the FastAPI application and ties together all components.
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
import logging
from contextlib import asynccontextmanager

from app.config import get_settings
from app.routers import api_router
from app.middleware import (
    RequestLoggingMiddleware,
    validation_exception_handler,
    hiregage_exception_handler,
    general_exception_handler
)
from app.utils.errors import HireGageError

# Configure logging
logging.basicConfig(
    level=logging.INFO if get_settings().DEBUG else logging.WARNING,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("hiregage")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Startup and shutdown events for the application
    """
    # Startup
    logger.info("Starting HireGage API Server...")
    # Load models, initialize services, etc.
    yield
    # Shutdown 
    logger.info("Shutting down HireGage API Server...")
    # Cleanup resources, close connections


# Initialize FastAPI application
app = FastAPI(
    title=get_settings().PROJECT_NAME,
    description="API for AI-powered HR interview agent",
    version=get_settings().VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_settings().CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add logging middleware
app.add_middleware(RequestLoggingMiddleware)

# Add exception handlers
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(HireGageError, hiregage_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Include API routers
app.include_router(api_router, prefix=get_settings().API_V1_STR)


# Root endpoint
@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "message": "Welcome to HireGage AI HR Interview Agent API",
        "version": get_settings().VERSION,
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
