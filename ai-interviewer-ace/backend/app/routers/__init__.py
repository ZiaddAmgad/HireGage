"""
Router package initialization
"""
from fastapi import APIRouter

from .interviews import router as interviews_router
from .system import router as system_router

# Create a main router to include all routers
api_router = APIRouter()

# Include all routers
api_router.include_router(interviews_router)
api_router.include_router(system_router)
