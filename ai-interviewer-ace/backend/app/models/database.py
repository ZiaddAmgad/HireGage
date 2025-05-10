"""
Database connection setup for the HireGage application
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

from app.config import get_settings

settings = get_settings()

# Check if we have a Database URL configured
if settings.DATABASE_URL:
    SQLALCHEMY_DATABASE_URL = str(settings.DATABASE_URL)
    # Create async engine
    engine = create_async_engine(
        SQLALCHEMY_DATABASE_URL, 
        echo=settings.DEBUG,
        future=True
    )
    
    # Create session factory
    SessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
        class_=AsyncSession
    )
else:
    # For development without database, create a mock engine/session
    engine = None
    SessionLocal = None


async def get_db():
    """Get database session dependency"""
    if SessionLocal is None:
        # Return None if database not configured
        return None
        
    db = SessionLocal()
    try:
        yield db
    finally:
        await db.close()
