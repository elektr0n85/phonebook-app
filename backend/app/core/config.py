"""
Application configuration using Pydantic Settings.
All settings loaded from environment variables.
"""
from pydantic_settings import BaseSettings
from pydantic import field_validator


class Settings(BaseSettings):
    """Application settings."""
    
    # Database
    DATABASE_URL: str
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:3000"
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 100
    LOGIN_RATE_LIMIT_PER_15MIN: int = 5
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # App Info
    PROJECT_NAME: str = "Phonebook API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Email / SMTP
    SMTP_HOST: str = "smtp.sendgrid.net"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    MAIL_FROM: str = "noreply@phonebook.com"
    MAIL_FROM_NAME: str = "Phonebook App"
    
    # Frontend URL (for password reset links)
    FRONTEND_URL: str = "http://localhost:5173"
    
    # Password reset
    RESET_TOKEN_EXPIRE_HOURS: int = 1
    
    @field_validator("SECRET_KEY")
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        """Validate SECRET_KEY length for security."""
        if len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long")
        return v
    
    @field_validator("ALLOWED_ORIGINS")
    @classmethod
    def parse_cors_origins(cls, v: str) -> list[str]:
        """Parse comma-separated CORS origins."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create global settings instance
settings = Settings()
