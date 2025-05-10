"""
Run script for HireGage backend server.
Supports development and production modes.
"""
import uvicorn
import argparse
import os
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("hiregage-server")

def main():
    """Run the FastAPI server with the specified configuration"""
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Run the HireGage API server")
    parser.add_argument(
        "--env",
        choices=["dev", "prod", "test"],
        default="dev",
        help="Environment to run in (dev, prod, test)",
    )
    parser.add_argument(
        "--host", 
        type=str, 
        default="0.0.0.0", 
        help="Host to bind the server to"
    )
    parser.add_argument(
        "--port", 
        type=int, 
        default=int(os.getenv("PORT", 8000)), 
        help="Port to bind the server to"
    )
    args = parser.parse_args()
    
    # Configure based on environment
    reload_enabled = args.env == "dev"
    workers = 1 if args.env == "dev" else (os.cpu_count() or 1) * 2 + 1
    log_level = "info" if args.env == "prod" else "debug"
    
    # Log configuration
    logger.info(f"Starting HireGage API server in {args.env} mode")
    logger.info(f"Host: {args.host}")
    logger.info(f"Port: {args.port}")
    logger.info(f"Workers: {workers}")
    logger.info(f"Reload enabled: {reload_enabled}")
    
    # Run the server
    uvicorn.run(
        "app.main:app",
        host=args.host,
        port=args.port,
        reload=reload_enabled,
        workers=workers,
        log_level=log_level
    )

if __name__ == "__main__":
    main()
