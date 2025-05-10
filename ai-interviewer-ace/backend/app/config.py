"""
Configuration module for HireGage AI Interviewer backend.
Handles environment variables, settings, and configuration validation.
"""
from pydantic_settings import BaseSettings
from pydantic import Field, validator, PostgresDsn
from typing import Optional, List, Dict, Any, Union
from functools import lru_cache
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    """Application settings with environment variable validation."""
    
    # API Configuration
    API_V1_STR: str = "/api/v1"
    API_PREFIX: str = "/api"  # Added for compatibility
    API_VERSION: str = "v1"   # Added for compatibility
    PROJECT_NAME: str = "HireGage AI HR Interview Agent"
    DEBUG: bool = Field(default=False)
    VERSION: str = "0.1.0"
    
    # Security
    SECRET_KEY: str = Field(..., description="Secret key for JWT token generation")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=60 * 24 * 7)  # 7 days
    
    # OpenAI Configuration
    OPENAI_API_KEY: str = Field(..., description="API key for OpenAI")
    OPENAI_MODEL: str = Field(default="gpt-4o")
    
    # Supabase Configuration
    SUPABASE_URL: str = Field(..., description="Supabase project URL")
    SUPABASE_KEY: str = Field(..., description="Supabase API key")
      # Database Configuration
    DATABASE_URL: Optional[PostgresDsn] = None
    
    # CORS Configuration
    CORS_ORIGINS: List[str] = Field(default=["http://localhost:5173", "http://localhost:3000", "http://localhost:5175"])
    
    # Interview Settings
    MAX_INTERVIEW_DURATION_MINUTES: int = Field(default=30)
    QUESTION_TIMEOUT_SECONDS: int = Field(default=60)
    
    # Optional TTS Configuration
    TTS_API_KEY: Optional[str] = None
    
    @validator("OPENAI_API_KEY", "SUPABASE_URL", "SUPABASE_KEY", "SECRET_KEY", pre=True)
    def check_not_empty(cls, v):
        if not v or len(str(v).strip()) == 0:
            raise ValueError("Missing required environment variable")
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Create cached instance of settings."""
    return Settings()