"""
Camera Stream Service - Main Application
Following FACEGUARD_V2_STRATEGIC_IMPLEMENTATION_GUIDE.md main application structure
"""
import asyncio
import logging
import sys
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Dict, Any

import structlog
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .config.settings import get_settings
from .services.camera_manager import CameraManager
from .api import health, cameras
from .api.health import set_camera_manager

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
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)

# Global camera manager instance
camera_manager: CameraManager = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan management
    Handles startup and shutdown procedures following strategic implementation guide
    """
    settings = get_settings()
    global camera_manager
    
    # ===== STARTUP =====
    logger.info("Starting Camera Stream Service", 
                service_name=settings.service_name,
                version=settings.service_version,
                port=settings.service_port)
    
    try:
        # Initialize camera manager
        logger.info("Initializing Camera Manager...")
        camera_manager = CameraManager(settings)
        await camera_manager.initialize()
        
        # Set camera manager for API endpoints
        set_camera_manager(camera_manager)
        
        # Auto-start streams if enabled
        if settings.enable_multi_camera:
            logger.info("Auto-starting camera streams...")
            await camera_manager.start_all_streams()
        
        logger.info("Camera Stream Service startup complete",
                   cameras_configured=len(camera_manager.cameras),
                   features_enabled={
                       "multi_camera": settings.enable_multi_camera,
                       "frame_quality_check": settings.enable_frame_quality_check,
                       "event_publishing": settings.enable_event_publishing,
                       "health_monitoring": settings.enable_health_monitoring,
                       "analytics": settings.enable_analytics
                   })
        
        yield
        
    except Exception as e:
        logger.error("Failed to start Camera Stream Service", error=str(e))
        sys.exit(1)
    
    # ===== SHUTDOWN =====
    logger.info("Shutting down Camera Stream Service...")
    
    try:
        if camera_manager:
            await camera_manager.shutdown()
        
        logger.info("Camera Stream Service shutdown complete")
        
    except Exception as e:
        logger.error("Error during shutdown", error=str(e))


def create_application() -> FastAPI:
    """
    Create and configure FastAPI application
    Following strategic implementation guide application structure
    """
    settings = get_settings()
    
    # Create FastAPI application
    app = FastAPI(
        title="Camera Stream Service",
        description="FaceGuard V2 Camera Stream Service - Real-time camera processing with face recognition integration",
        version=settings.service_version,
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json"
    )
    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "http://localhost:8000", "http://localhost:8001", "http://localhost:8002"],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["*"],
    )
    
    # Include API routers
    app.include_router(health.router, prefix="/api/health", tags=["Health Monitoring"])
    app.include_router(cameras.router, prefix="/api/cameras", tags=["Camera Management"])
    
    # Also include health endpoints at root level for compatibility
    app.include_router(health.router, prefix="/health", tags=["Health Monitoring - Root Level"])
    app.include_router(cameras.router, prefix="/cameras", tags=["Camera Management - Root Level"])
    
    # Root endpoint
    @app.get("/")
    async def root() -> Dict[str, Any]:
        """
        Service information endpoint
        Returns service details and current status
        """
        global camera_manager
        
        # Get basic service info
        service_info = {
            "service": settings.service_name,
            "version": settings.service_version,
            "description": "FaceGuard V2 Camera Stream Service",
            "timestamp": datetime.utcnow().isoformat(),
            "status": "initializing"
        }
        
        # Add camera manager status if available
        if camera_manager:
            try:
                health_summary = camera_manager.get_health_summary()
                service_info.update({
                    "status": health_summary["status"],
                    "cameras_configured": health_summary["total_cameras"],
                    "cameras_connected": health_summary["connected_cameras"],
                    "active_streams": health_summary["active_streams"],
                    "uptime_seconds": health_summary["uptime_seconds"]
                })
            except Exception as e:
                service_info["status"] = "error"
                service_info["error"] = str(e)
        
        # Add feature flags
        service_info["features"] = {
            "multi_camera": settings.enable_multi_camera,
            "frame_quality_check": settings.enable_frame_quality_check,
            "event_publishing": settings.enable_event_publishing,
            "health_monitoring": settings.enable_health_monitoring,
            "analytics": settings.enable_analytics
        }
        
        # Add configuration summary
        service_info["configuration"] = {
            "max_concurrent_cameras": settings.max_concurrent_cameras,
            "frame_rate": settings.camera_frame_rate,
            "frame_buffer_size": settings.frame_buffer_size,
            "memory_limit_mb": settings.memory_limit_mb,
            "integration_services": {
                "core_data_service": settings.core_data_service_url,
                "face_recognition_service": settings.face_recognition_service_url
            }
        }
        
        return service_info
    
    # Global exception handler
    @app.exception_handler(Exception)
    async def global_exception_handler(request, exc):
        """
        Global exception handler for proper error responses
        Following strategic implementation guide error handling
        """
        logger.error("Unhandled exception",
                    path=str(request.url.path),
                    method=request.method,
                    error=str(exc),
                    exc_info=True)
        
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "message": "An unexpected error occurred",
                "timestamp": datetime.utcnow().isoformat(),
                "path": str(request.url.path)
            }
        )
    
    return app


# Create application instance
app = create_application()


if __name__ == "__main__":
    import uvicorn
    
    settings = get_settings()
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, settings.log_level),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Run application
    uvicorn.run(
        "main:app",
        host=settings.service_host,
        port=settings.service_port,
        log_level=settings.log_level.lower(),
        reload=False,  # Disable reload in production
        access_log=True
    )