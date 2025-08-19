"""
FACEGUARD V2 CORE DATA SERVICE - MAIN APPLICATION
Rule 2: Zero Placeholder Code - Real FastAPI application
Rule 3: Error-First Development - Comprehensive error handling
Rule 1: Incremental Completeness - Service A foundation first
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import structlog
import sys
import asyncio
from pathlib import Path

# Add src to Python path for imports
sys.path.append(str(Path(__file__).parent))

from config.settings import get_settings
from storage.database import get_database_manager
from api.health import router as health_router
from api.persons import router as persons_router
from api.sightings import router as sightings_router
from api.notifications import router as notifications_router
from api.high_priority_persons import router as high_priority_persons_router
from api.notification_contacts import router as notification_contacts_router
from api.websocket import router as websocket_router
from api.video_processing import router as video_processing_router

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application startup and shutdown handlers
    Rule 3: Error-First Development - Proper initialization validation
    """
    
    # Startup
    await logger.ainfo("Starting FaceGuard V2 Core Data Service", version=settings.service_version)
    
    try:
        # Initialize database connection
        db_manager = await get_database_manager()
        
        # Test database connectivity
        health_status = await db_manager.health_check()
        if health_status.get("status") != "healthy":
            await logger.aerror("Database connection failed during startup", details=health_status)
            raise Exception(f"Database startup validation failed: {health_status}")
        
        await logger.ainfo("Database connection validated", response_time=health_status.get("response_time_ms"))
        
        # Initialize database schema (if needed)
        try:
            await db_manager.initialize_database()
            await logger.ainfo("Database schema initialization completed")
        except Exception as e:
            await logger.awarn("Database schema initialization skipped", reason=str(e))
        
        # Validate feature flags
        feature_status = {
            "analytics": settings.enable_analytics,
            "faiss": settings.enable_faiss,
            "migration": settings.enable_migration,
            "health_checks": settings.enable_health_checks
        }
        await logger.ainfo("Feature flags configured", features=feature_status)
        
        # Validate FAISS configuration (if enabled)
        if settings.enable_faiss:
            try:
                import faiss
                await logger.ainfo("FAISS library available", version=getattr(faiss, '__version__', 'unknown'))
            except ImportError:
                await logger.awarn("FAISS library not installed - vector operations will be disabled")
        
        await logger.ainfo("Core Data Service startup completed successfully")
        
        yield  # Application is running
        
    except Exception as e:
        await logger.aerror("Core Data Service startup failed", error=str(e))
        raise
    
    # Shutdown
    await logger.ainfo("Shutting down Core Data Service")
    try:
        db_manager = await get_database_manager()
        await db_manager.close()
        await logger.ainfo("Database connections closed successfully")
    except Exception as e:
        await logger.aerror("Error during shutdown", error=str(e))


# Create FastAPI application
app = FastAPI(
    title="FaceGuard V2 Core Data Service",
    description="""
    Core Data Service for FaceGuard V2 - Database operations, analytics, and FAISS vector storage.
    
    **Architecture Philosophy:**
    - Rule 1: Incremental Completeness - This service is 100% functional before others
    - Rule 2: Zero Placeholder Code - All endpoints are real implementations
    - Rule 3: Error-First Development - Proper HTTP codes, no error hiding
    - Rule 4: End-to-End Before Features - Simple workflow first
    """,
    version=settings.service_version,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # Command Center
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health_router)
app.include_router(persons_router)
app.include_router(sightings_router)
app.include_router(notifications_router)
app.include_router(high_priority_persons_router)
app.include_router(notification_contacts_router)
app.include_router(websocket_router)
app.include_router(video_processing_router)

# Root endpoint
@app.get("/", tags=["root"])
async def root():
    """
    Root endpoint - Service information
    Rule 2: Zero Placeholder Code - Real service metadata
    """
    return {
        "service": "core-data-service",
        "version": settings.service_version,
        "status": "operational",
        "architecture": "FaceGuard V2",
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "openapi": "/openapi.json"
        },
        "features": {
            "analytics": settings.enable_analytics,
            "faiss": settings.enable_faiss,
            "migration": settings.enable_migration,
            "health_checks": settings.enable_health_checks
        }
    }

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    Global exception handler
    Rule 3: Error-First Development - Never hide errors
    """
    await logger.aerror("Unhandled exception", error=str(exc), path=str(request.url))
    
    return HTTPException(
        status_code=500,
        detail={
            "error": "Internal server error",
            "message": str(exc),
            "service": "core-data-service",
            "timestamp": structlog.get_logger().info("Getting timestamp")
        }
    )

if __name__ == "__main__":
    import uvicorn
    
    # Run with uvicorn
    uvicorn.run(
        "main:app",
        host=settings.service_host,
        port=settings.service_port,
        reload=False,  # Disable reload for production stability
        log_level=settings.log_level.lower(),
        access_log=True
    )