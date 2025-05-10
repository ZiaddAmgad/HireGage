"""
Error handling utilities for the HireGage application
"""
from fastapi import HTTPException, status
from typing import Dict, Any, Optional


class HireGageError(Exception):
    """Base exception class for HireGage application"""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class AIServiceError(HireGageError):
    """Exception when AI service (e.g. OpenAI) fails"""
    def __init__(self, message: str, service_error: Optional[Exception] = None):
        self.service_error = service_error
        super().__init__(f"AI service error: {message}")


class DatabaseError(HireGageError):
    """Exception when database operations fail"""
    def __init__(self, message: str, db_error: Optional[Exception] = None):
        self.db_error = db_error
        super().__init__(f"Database error: {message}")


class ValidationError(HireGageError):
    """Exception when input validation fails"""
    def __init__(self, message: str, validation_errors: Optional[Dict[str, Any]] = None):
        self.validation_errors = validation_errors or {}
        super().__init__(f"Validation error: {message}")


def http_error_handler(error: HireGageError) -> HTTPException:
    """Convert application errors to FastAPI HTTP exceptions"""
    if isinstance(error, AIServiceError):
        return HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"message": error.message, "type": "ai_service_error"}
        )
    elif isinstance(error, DatabaseError):
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": error.message, "type": "database_error"}
        )
    elif isinstance(error, ValidationError):
        return HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"message": error.message, "errors": error.validation_errors, "type": "validation_error"}
        )
    else:
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": error.message, "type": "internal_error"}
        )
