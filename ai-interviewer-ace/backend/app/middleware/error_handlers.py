"""
Error handling middleware
"""
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.utils.errors import HireGageError, http_error_handler
import logging

# Set up logging
logger = logging.getLogger("hiregage")

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handle validation errors from request body/parameters
    """
    logger.warning(f"Validation error: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": exc.errors(),
            "body": exc.body,
            "message": "Request validation error"
        },
    )

async def hiregage_exception_handler(request: Request, exc: HireGageError):
    """
    Handle application-specific errors
    """
    http_exception = http_error_handler(exc)
    return JSONResponse(
        status_code=http_exception.status_code,
        content=http_exception.detail,
    )

async def general_exception_handler(request: Request, exc: Exception):
    """
    Handle all other exceptions
    """
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "message": "Internal server error",
            "detail": str(exc) if str(exc) else "Unknown error"
        },
    )
