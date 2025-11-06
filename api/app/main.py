"""
FastAPI application entry point.
Main application configuration and router setup.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from config import get_settings
from database import engine, Base
from api.v1 import auth, tenants, users, volunteers, events, reports, integrations
import os

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup: Create database tables
    Base.metadata.create_all(bind=engine)
    print("✓ Database tables created")
    
    yield
    
    # Shutdown: Cleanup
    print("✓ Application shutdown")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Virginia Volunteer Health System - Multi-tenant SaaS for volunteer management",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan
)

origins = os.getenv("CORS_ORIGINS", "https://vvhs-saas.sitevision.com").split(",")


# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION
    }


# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(tenants.router, prefix="/api/v1/tenants", tags=["Tenants"])
app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(volunteers.router, prefix="/api/v1/volunteers", tags=["Volunteers"])
app.include_router(events.router, prefix="/api/v1/events", tags=["Events"])
app.include_router(reports.router, prefix="/api/v1/reports", tags=["Reports"])
app.include_router(integrations.router, prefix="/api/v1/integrations", tags=["Integrations"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
