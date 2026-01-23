"""
Pydantic schemas for authentication - JWT tokens and responses.
"""
from pydantic import BaseModel


class Token(BaseModel):
    """
    Schema for JWT token response.
    
    Security: Standard OAuth2 token response format
    """
    
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """
    Schema for JWT token payload data.
    
    Security: Minimal data in token (only user email)
    """
    
    email: str | None = None


class TokenRefresh(BaseModel):
    """Schema for refresh token request."""
    
    refresh_token: str


class TokenPair(BaseModel):
    """
    Schema for both access and refresh tokens.
    
    Security:
        - access_token: Short-lived (30 min)
        - refresh_token: Longer-lived (7 days)
    """
    
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class MessageResponse(BaseModel):
    """Generic message response schema."""
    
    message: str


class ErrorResponse(BaseModel):
    """Generic error response schema."""
    
    detail: str
