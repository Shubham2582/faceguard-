"""
Health monitoring API endpoints
Following FACEGUARD_V2_STRATEGIC_IMPLEMENTATION_GUIDE.md health check implementation strategy
"""
import psutil
import asyncio
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, Optional

from ..domain.models import ServiceHealth
from ..services.camera_manager import CameraManager
from ..config.settings import Settings, get_settings

router = APIRouter()

# Global camera manager instance
camera_manager: Optional[CameraManager] = None


def get_camera_manager() -> CameraManager:
    """Get camera manager instance"""
    global camera_manager
    if camera_manager is None:
        raise HTTPException(status_code=503, detail="Camera manager not initialized")
    return camera_manager


def set_camera_manager(manager: CameraManager):
    """Set camera manager instance"""
    global camera_manager
    camera_manager = manager


@router.get("/", response_model=Dict[str, Any])
async def health_check(
    settings: Settings = Depends(get_settings),
    manager: CameraManager = Depends(get_camera_manager)
):
    """
    Comprehensive health check endpoint
    Returns detailed service status following strategic implementation guide
    """
    try:
        # Get current timestamp
        timestamp = datetime.utcnow()
        
        # Get camera manager health summary
        camera_health = manager.get_health_summary()
        
        # Get system metrics
        memory_info = psutil.virtual_memory()
        memory_usage_mb = memory_info.used / 1024 / 1024
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # Calculate service uptime
        uptime_seconds = camera_health["uptime_seconds"]
        
        # Determine overall status
        status = "healthy"
        if camera_health["total_cameras"] == 0:
            status = "degraded"
        elif camera_health["connected_cameras"] == 0:
            status = "unhealthy"
        elif camera_health["total_errors"] > camera_health["total_frames_processed"] * 0.1:
            status = "degraded"  # More than 10% error rate
        
        # Create health response
        health_data = ServiceHealth(
            status=status,
            timestamp=timestamp,
            uptime_seconds=uptime_seconds,
            cameras_total=camera_health["total_cameras"],
            cameras_active=camera_health["active_streams"],
            cameras_connected=camera_health["connected_cameras"],
            frames_processed_total=camera_health["total_frames_processed"],
            events_published_total=0,  # Will be updated when event system is implemented
            memory_usage_mb=memory_usage_mb,
            cpu_usage_percent=cpu_percent,
            errors_count=camera_health["total_errors"]
        )
        
        # Build comprehensive response
        response = {
            "service": {
                "name": settings.service_name,
                "version": settings.service_version,
                "status": status,
                "timestamp": timestamp.isoformat(),
                "uptime_seconds": uptime_seconds
            },
            "components": {
                "camera_manager": {
                    "status": camera_health["status"],
                    "total_cameras": camera_health["total_cameras"],
                    "connected_cameras": camera_health["connected_cameras"],
                    "active_streams": camera_health["active_streams"],
                    "frames_processed": camera_health["total_frames_processed"],
                    "errors": camera_health["total_errors"]
                },
                "system": {
                    "memory_usage_mb": round(memory_usage_mb, 2),
                    "memory_usage_percent": round(memory_info.percent, 2),
                    "cpu_usage_percent": round(cpu_percent, 2),
                    "available_memory_mb": round((memory_info.available / 1024 / 1024), 2)
                },
                "configuration": {
                    "max_concurrent_cameras": settings.max_concurrent_cameras,
                    "frame_rate": settings.camera_frame_rate,
                    "frame_buffer_size": settings.frame_buffer_size,
                    "enable_frame_quality_check": settings.enable_frame_quality_check,
                    "enable_event_publishing": settings.enable_event_publishing,
                    "enable_health_monitoring": settings.enable_health_monitoring
                }
            },
            "cameras": []
        }
        
        # Add individual camera status
        for camera_info in manager.get_all_cameras_info():
            camera_status = {
                "camera_id": camera_info.camera_id,
                "name": camera_info.configuration.name,
                "source": camera_info.configuration.source,
                "status": camera_info.status.value if hasattr(camera_info.status, 'value') else camera_info.status,
                "stream_status": camera_info.stream_status.value if hasattr(camera_info.stream_status, 'value') else camera_info.stream_status,
                "frames_processed": camera_info.frames_processed,
                "errors_count": camera_info.errors_count,
                "last_frame_time": camera_info.last_frame_time.isoformat() if camera_info.last_frame_time else None,
                "uptime_seconds": camera_info.uptime_seconds,
                "last_error": camera_info.last_error
            }
            response["cameras"].append(camera_status)
        
        return response
        
    except Exception as e:
        # Log error but return degraded status instead of failing
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Health check error: {str(e)}")
        
        return {
            "service": {
                "name": settings.service_name,
                "version": settings.service_version,
                "status": "unhealthy",
                "timestamp": datetime.utcnow().isoformat(),
                "error": str(e)
            },
            "components": {
                "error": "Health check failed"
            }
        }


@router.get("/live")
async def liveness_probe():
    """
    Simple liveness probe for container orchestration
    Returns 200 if service is running
    """
    return {"status": "alive", "timestamp": datetime.utcnow().isoformat()}


@router.get("/ready")
async def readiness_probe(
    manager: CameraManager = Depends(get_camera_manager)
):
    """
    Readiness probe - checks if service is ready to handle requests
    Returns 200 if cameras are initialized and at least one is connected
    """
    try:
        health_summary = manager.get_health_summary()
        
        # Service is ready if:
        # 1. Camera manager is initialized
        # 2. At least one camera is configured
        # 3. No critical errors preventing operation
        
        if health_summary["total_cameras"] == 0:
            raise HTTPException(
                status_code=503, 
                detail="No cameras configured"
            )
        
        # Check if any cameras are functional
        cameras_info = manager.get_all_cameras_info()
        functional_cameras = sum(
            1 for cam in cameras_info 
            if cam.status in ["connected", "connecting"]
        )
        
        if functional_cameras == 0:
            raise HTTPException(
                status_code=503,
                detail="No functional cameras available"
            )
        
        return {
            "status": "ready",
            "timestamp": datetime.utcnow().isoformat(),
            "cameras_configured": health_summary["total_cameras"],
            "cameras_functional": functional_cameras
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Readiness check failed: {str(e)}"
        )


@router.get("/cameras/{camera_id}/health")
async def camera_health_check(
    camera_id: str,
    manager: CameraManager = Depends(get_camera_manager)
):
    """
    Health check for specific camera
    Returns detailed camera status and diagnostics
    """
    camera_info = manager.get_camera_info(camera_id)
    
    if camera_info is None:
        raise HTTPException(
            status_code=404,
            detail=f"Camera {camera_id} not found"
        )
    
    # Perform connection test if camera is not connected
    connection_test_result = None
    if camera_info.status != "connected":
        try:
            # Attempt to connect to get current status
            connection_test_result = await manager.connect_camera(camera_id)
        except Exception as e:
            connection_test_result = f"Connection test failed: {str(e)}"
    
    return {
        "camera_id": camera_id,
        "status": camera_info.status.value if hasattr(camera_info.status, 'value') else camera_info.status,
        "configuration": {
            "name": camera_info.configuration.name,
            "source": camera_info.configuration.source,
            "camera_type": camera_info.configuration.camera_type.value if hasattr(camera_info.configuration.camera_type, 'value') else camera_info.configuration.camera_type,
            "resolution": f"{camera_info.configuration.resolution_width}x{camera_info.configuration.resolution_height}",
            "frame_rate": camera_info.configuration.frame_rate,
            "enabled": camera_info.configuration.enabled
        },
        "statistics": {
            "frames_processed": camera_info.frames_processed,
            "frames_recognized": camera_info.frames_recognized,
            "errors_count": camera_info.errors_count,
            "uptime_seconds": camera_info.uptime_seconds,
            "last_frame_time": camera_info.last_frame_time.isoformat() if camera_info.last_frame_time else None
        },
        "diagnostics": {
            "last_error": camera_info.last_error,
            "connection_test": connection_test_result,
            "stream_status": camera_info.stream_status.value if hasattr(camera_info.stream_status, 'value') else camera_info.stream_status,
            "auto_reconnect": camera_info.configuration.auto_reconnect
        },
        "timestamp": datetime.utcnow().isoformat()
    }


@router.post("/cameras/{camera_id}/test-connection")
async def test_camera_connection(
    camera_id: str,
    manager: CameraManager = Depends(get_camera_manager)
):
    """
    Test camera connection and return detailed results
    Useful for troubleshooting camera configuration issues
    """
    camera_info = manager.get_camera_info(camera_id)
    
    if camera_info is None:
        raise HTTPException(
            status_code=404,
            detail=f"Camera {camera_id} not found"
        )
    
    try:
        start_time = datetime.utcnow()
        
        # Attempt connection
        success = await manager.connect_camera(camera_id)
        
        end_time = datetime.utcnow()
        connection_time_ms = (end_time - start_time).total_seconds() * 1000
        
        if success:
            # Try to capture a test frame
            try:
                frame_data = await manager.get_frame(camera_id, timeout=5.0)
                frame_captured = frame_data is not None
                
                if frame_captured:
                    frame, metadata = frame_data
                    frame_info = {
                        "width": metadata.width,
                        "height": metadata.height,
                        "channels": metadata.channels,
                        "size_bytes": metadata.file_size,
                        "quality_score": metadata.quality_score,
                        "quality_grade": metadata.quality_grade.value if metadata.quality_grade and hasattr(metadata.quality_grade, 'value') else (metadata.quality_grade if metadata.quality_grade else None)
                    }
                else:
                    frame_info = None
                    
            except Exception as e:
                frame_captured = False
                frame_info = {"error": str(e)}
            
            return {
                "camera_id": camera_id,
                "connection_successful": True,
                "connection_time_ms": round(connection_time_ms, 2),
                "frame_captured": frame_captured,
                "frame_info": frame_info,
                "timestamp": datetime.utcnow().isoformat(),
                "message": "Camera connection test successful"
            }
        else:
            # Get error details
            updated_info = manager.get_camera_info(camera_id)
            
            return {
                "camera_id": camera_id,
                "connection_successful": False,
                "connection_time_ms": round(connection_time_ms, 2),
                "error": updated_info.last_error if updated_info else "Unknown error",
                "timestamp": datetime.utcnow().isoformat(),
                "message": "Camera connection test failed"
            }
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Connection test failed: {str(e)}"
        )