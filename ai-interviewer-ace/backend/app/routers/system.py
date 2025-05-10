"""
API router for health and system endpoints
"""
from fastapi import APIRouter, Depends
import time
import platform
import sys

from app.config import get_settings

router = APIRouter(
    prefix="/system",
    tags=["system"],
)


@router.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring and load balancers
    
    Returns basic system health information and API status
    """
    settings = get_settings()
    return {
        "status": "healthy", 
        "timestamp": time.time(),
        "environment": "development" if settings.DEBUG else "production",
        "api_version": settings.VERSION
    }


@router.get("/info")
async def system_info():
    """
    System information endpoint
    
    Returns information about the system environment.
    Only available in debug mode.
    """
    settings = get_settings()
    
    # Only provide detailed info in debug mode
    if not settings.DEBUG:
        return {"message": "System information only available in debug mode"}
        
    return {
        "api_version": settings.VERSION,
        "project_name": settings.PROJECT_NAME,
        "python_version": sys.version,
        "platform": platform.platform(),
        "debug_mode": settings.DEBUG,
    }
