"""
Middleware for logging requests and responses
"""
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import time
import logging
import uuid

# Set up logging
logger = logging.getLogger("hiregage")

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging requests and responses"""
    
    async def dispatch(self, request: Request, call_next):
        """Process request and log details"""
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # Log request
        logger.info(f"Request [{request_id}]: {request.method} {request.url.path}")
        
        # Process request and time it
        start_time = time.time()
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            
            # Log response
            logger.info(
                f"Response [{request_id}]: {response.status_code} "
                f"completed in {process_time:.3f}s"
            )
            
            # Add headers
            response.headers["X-Process-Time"] = str(process_time)
            response.headers["X-Request-ID"] = request_id
            
            return response
            
        except Exception as e:
            # Log errors
            process_time = time.time() - start_time
            logger.error(
                f"Error [{request_id}]: {str(e)} "
                f"after {process_time:.3f}s"
            )
            raise
