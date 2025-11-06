"""
Application configuration using Pydantic Settings.
Environment variables are loaded from .env file.
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Application
    APP_NAME: str = "VVHS - Virginia Volunteer Health System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Database # Host should be in environment var but is @vvhs-db
    DATABASE_URL: str = "postgresql://vvhs:vvhs_password@vvhs-db:5432/vvhs_db"
    
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS
    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:5173"]
    
    # TRAIN Integration (placeholder)
    TRAIN_API_URL: str = "https://api.train.org/v1"  # TODO: Add real TRAIN API endpoint
    TRAIN_API_KEY: str = "placeholder-api-key"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
