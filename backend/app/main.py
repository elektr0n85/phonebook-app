"""
FastAPI application entry point.
Includes security middleware, CORS, and API routing.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings

# Create FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Secure Phonebook API with JWT authentication",
    docs_url="/docs" if settings.DEBUG else None,  # Disable docs in production
    redoc_url="/redoc" if settings.DEBUG else None,
)


# ============================================================================
# MIDDLEWARE CONFIGURATION
# ============================================================================

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost",
        "http://localhost:80",
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1",
    ], #allow_origins=settings.ALLOWED_ORIGINS,  # Whitelist only
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],  # Explicit methods only
    allow_headers=["Authorization", "Content-Type"],  # Explicit headers only
    max_age=3600,  # Cache preflight requests for 1 hour
)


# Security Headers Middleware
@app.middleware("http")
async def add_security_headers(request, call_next):
    """
    Add security headers to all responses.
    
    Security headers:
        - X-Content-Type-Options: Prevent MIME sniffing
        - X-Frame-Options: Prevent clickjacking
        - X-XSS-Protection: Enable XSS filter
        - Strict-Transport-Security: Enforce HTTPS
        - Content-Security-Policy: Prevent XSS
        - Referrer-Policy: Control referrer information
        - Permissions-Policy: Disable dangerous features
    """
    response = await call_next(request)
    
    # Prevent MIME type sniffing
    response.headers["X-Content-Type-Options"] = "nosniff"
    
    # Prevent clickjacking
    response.headers["X-Frame-Options"] = "DENY"
    
    # Enable XSS protection
    response.headers["X-XSS-Protection"] = "1; mode=block"
    
    # Enforce HTTPS (only in production)
    if not settings.DEBUG:
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains; preload"
        )
    
    # Content Security Policy
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data: https:; "
        "font-src 'self'; "
        "connect-src 'self'; "
        "frame-ancestors 'none';"
    )
    
    # Referrer policy
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    
    # Permissions policy (disable dangerous features)
    response.headers["Permissions-Policy"] = (
        "geolocation=(), microphone=(), camera=(), payment=()"
    )
    
    return response


# ============================================================================
# API ROUTES
# ============================================================================

# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint.
    
    Returns:
        Status and version information
        
    Security: Public endpoint (no authentication)
    """
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
    }


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint with API information.
    
    Returns:
        Welcome message and API documentation link
    """
    return {
        "message": "Welcome to Phonebook API",
        "version": settings.VERSION,
        "docs": "/docs" if settings.DEBUG else "Documentation disabled in production",
    }


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.exception_handler(404)
async def not_found_handler(request, exc):
    """
    Custom 404 handler.
    
    Security: Generic message (no information disclosure)
    """
    return JSONResponse(
        status_code=404,
        content={"detail": "Resource not found"},
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """
    Custom 500 handler.
    
    Security: Generic message (no stack trace in production)
    """
    if settings.DEBUG:
        # In development, show error details
        return JSONResponse(
            status_code=500,
            content={"detail": str(exc)},
        )
    else:
        # In production, generic message only
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"},
        )


# ============================================================================
# APPLICATION LIFECYCLE
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """
    Application startup event.
    
    Actions:
        - Log startup
        - Initialize connections (if needed)
        - Run health checks
    """
    print(f"🚀 Starting {settings.PROJECT_NAME} v{settings.VERSION}")
    print(f"📝 Environment: {settings.ENVIRONMENT}")
    print(f"🔒 CORS Origins: {settings.ALLOWED_ORIGINS}")
    
    # TODO: Add database connection check

    # TODO: Add Redis connection check (if using)


@app.on_event("shutdown")
async def shutdown_event():
    """
    Application shutdown event.
    
    Actions:
        - Close database connections
        - Cleanup resources
        - Log shutdown
    """
    print(f"👋 Shutting down {settings.PROJECT_NAME}")


# ============================================================================
# INCLUDE ROUTERS
# ============================================================================

from app.api.v1 import admin, auth, contacts, users

app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["Authentication"])
app.include_router(users.router, prefix=f"{settings.API_V1_STR}/users", tags=["Users"])
app.include_router(contacts.router, prefix=f"{settings.API_V1_STR}/contacts", tags=["Contacts"])
app.include_router(admin.router, prefix=f"{settings.API_V1_STR}/admin", tags=["Admin"])


if __name__ == "__main__":
    import uvicorn
    
    # Run with: python -m app.main
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="debug" if settings.DEBUG else "info",
    )
