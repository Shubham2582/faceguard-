"""
Camera management API endpoints
Following FACEGUARD_V2_STRATEGIC_IMPLEMENTATION_GUIDE.md API design principles
"""
from datetime import datetime
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
import base64
import cv2
import numpy as np
import logging

logger = logging.getLogger(__name__)

from ..domain.models import (
    CameraInfo, CameraCreateRequest, CameraUpdateRequest, 
    StreamControlRequest, ServiceStats
)
from ..services.camera_manager import CameraManager
from ..config.settings import Settings, get_settings
from .health import get_camera_manager

router = APIRouter()


@router.get("/", response_model=List[CameraInfo])
async def list_cameras(
    manager: CameraManager = Depends(get_camera_manager)
):
    """
    List all configured cameras with their current status
    Returns comprehensive camera information
    """
    try:
        cameras_info = manager.get_all_cameras_info()
        return cameras_info
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve cameras: {str(e)}"
        )


@router.post("/", response_model=Dict[str, Any])
async def create_camera(
    request: CameraCreateRequest,
    manager: CameraManager = Depends(get_camera_manager)
):
    """
    Add new camera configuration
    Automatically detects camera type and attempts connection
    """
    try:
        # Add camera to manager
        camera_id = await manager.add_camera(
            source=request.source,
            name=request.name,
            location=request.location
        )
        
        # Attempt initial connection
        connection_success = await manager.connect_camera(camera_id)
        
        # Get camera info
        camera_info = manager.get_camera_info(camera_id)
        
        return {
            "camera_id": camera_id,
            "name": request.name,
            "source": request.source,
            "connection_successful": connection_success,
            "status": camera_info.status.value if camera_info else "unknown",
            "message": f"Camera {camera_id} created successfully",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create camera: {str(e)}"
        )


@router.get("/{camera_id}", response_model=CameraInfo)
async def get_camera(
    camera_id: str,
    manager: CameraManager = Depends(get_camera_manager)
):
    """
    Get detailed information for specific camera
    """
    camera_info = manager.get_camera_info(camera_id)
    
    if camera_info is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Camera {camera_id} not found"
        )
    
    return camera_info


@router.put("/{camera_id}", response_model=Dict[str, Any])
async def update_camera(
    camera_id: str,
    request: CameraUpdateRequest,
    manager: CameraManager = Depends(get_camera_manager)
):
    """
    Update camera configuration
    Note: Camera must be disconnected before updating source/resolution
    """
    camera_info = manager.get_camera_info(camera_id)
    
    if camera_info is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Camera {camera_id} not found"
        )
    
    try:
        # Get current camera configuration
        camera = manager.cameras[camera_id]
        config = camera.config
        
        # Update configuration fields
        if request.name is not None:
            config.name = request.name
        if request.location is not None:
            config.location = request.location
        if request.resolution_width is not None:
            config.resolution_width = request.resolution_width
        if request.resolution_height is not None:
            config.resolution_height = request.resolution_height
        if request.frame_rate is not None:
            config.frame_rate = request.frame_rate
        if request.enabled is not None:
            config.enabled = request.enabled
            
            # If disabling camera, stop stream
            if not request.enabled:
                await manager.stop_stream(camera_id)
                await manager.disconnect_camera(camera_id)
        
        return {
            "camera_id": camera_id,
            "message": f"Camera {camera_id} updated successfully",
            "updated_fields": [
                field for field, value in request.dict(exclude_unset=True).items()
                if value is not None
            ],
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to update camera: {str(e)}"
        )


@router.delete("/{camera_id}")
async def delete_camera(
    camera_id: str,
    manager: CameraManager = Depends(get_camera_manager)
):
    """
    Remove camera configuration
    Stops stream and disconnects camera before removal
    """
    camera_info = manager.get_camera_info(camera_id)
    
    if camera_info is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Camera {camera_id} not found"
        )
    
    try:
        # Stop stream and disconnect
        await manager.stop_stream(camera_id)
        await manager.disconnect_camera(camera_id)
        
        # Remove from manager
        del manager.cameras[camera_id]
        del manager.frame_queues[camera_id]
        del manager.running_streams[camera_id]
        
        return {
            "camera_id": camera_id,
            "message": f"Camera {camera_id} deleted successfully",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete camera: {str(e)}"
        )


@router.post("/{camera_id}/connect")
async def connect_camera(
    camera_id: str,
    manager: CameraManager = Depends(get_camera_manager)
):
    """
    Connect specific camera
    Tests connection and reports detailed results
    """
    camera_info = manager.get_camera_info(camera_id)
    
    if camera_info is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Camera {camera_id} not found"
        )
    
    try:
        start_time = datetime.utcnow()
        success = await manager.connect_camera(camera_id)
        end_time = datetime.utcnow()
        
        connection_time_ms = (end_time - start_time).total_seconds() * 1000
        
        # Get updated camera info
        updated_info = manager.get_camera_info(camera_id)
        
        if success:
            return {
                "camera_id": camera_id,
                "connection_successful": True,
                "connection_time_ms": round(connection_time_ms, 2),
                "status": updated_info.status.value,
                "message": f"Camera {camera_id} connected successfully",
                "timestamp": datetime.utcnow().isoformat()
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={
                    "camera_id": camera_id,
                    "connection_successful": False,
                    "connection_time_ms": round(connection_time_ms, 2),
                    "error": updated_info.last_error,
                    "message": f"Failed to connect camera {camera_id}",
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Connection attempt failed: {str(e)}"
        )


@router.post("/{camera_id}/disconnect")
async def disconnect_camera(
    camera_id: str,
    manager: CameraManager = Depends(get_camera_manager)
):
    """
    Disconnect specific camera
    Stops stream if running and closes camera connection
    """
    camera_info = manager.get_camera_info(camera_id)
    
    if camera_info is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Camera {camera_id} not found"
        )
    
    try:
        # Stop stream if running
        await manager.stop_stream(camera_id)
        
        # Disconnect camera
        await manager.disconnect_camera(camera_id)
        
        return {
            "camera_id": camera_id,
            "message": f"Camera {camera_id} disconnected successfully",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to disconnect camera: {str(e)}"
        )


@router.post("/streams/control")
async def control_streams(
    request: StreamControlRequest,
    manager: CameraManager = Depends(get_camera_manager)
):
    """
    Control camera streams (start, stop, pause, resume)
    Can target specific cameras or all cameras
    """
    try:
        action = request.action.lower()
        camera_ids = request.camera_ids or list(manager.cameras.keys())
        
        results = []
        
        for camera_id in camera_ids:
            if camera_id not in manager.cameras:
                results.append({
                    "camera_id": camera_id,
                    "success": False,
                    "error": f"Camera {camera_id} not found"
                })
                continue
            
            try:
                if action == "start":
                    success = await manager.start_stream(camera_id)
                    results.append({
                        "camera_id": camera_id,
                        "success": success,
                        "action": "start",
                        "message": "Stream started" if success else "Failed to start stream"
                    })
                    
                elif action == "stop":
                    await manager.stop_stream(camera_id)
                    results.append({
                        "camera_id": camera_id,
                        "success": True,
                        "action": "stop",
                        "message": "Stream stopped"
                    })
                    
                elif action == "pause":
                    # Pause by stopping stream but keeping connection
                    await manager.stop_stream(camera_id)
                    results.append({
                        "camera_id": camera_id,
                        "success": True,
                        "action": "pause",
                        "message": "Stream paused"
                    })
                    
                elif action == "resume":
                    # Resume by starting stream
                    success = await manager.start_stream(camera_id)
                    results.append({
                        "camera_id": camera_id,
                        "success": success,
                        "action": "resume",
                        "message": "Stream resumed" if success else "Failed to resume stream"
                    })
                    
                else:
                    results.append({
                        "camera_id": camera_id,
                        "success": False,
                        "error": f"Unknown action: {action}"
                    })
                    
            except Exception as e:
                results.append({
                    "camera_id": camera_id,
                    "success": False,
                    "error": str(e)
                })
        
        # Count successes
        successful_operations = sum(1 for result in results if result.get("success", False))
        
        return {
            "action": action,
            "cameras_targeted": len(camera_ids),
            "successful_operations": successful_operations,
            "results": results,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Stream control failed: {str(e)}"
        )


@router.get("/stats/summary")
async def get_service_stats(
    manager: CameraManager = Depends(get_camera_manager),
    settings: Settings = Depends(get_settings)
):
    """
    Get comprehensive service statistics
    Includes camera status, processing metrics, and performance data
    """
    try:
        # Get camera health summary
        health_summary = manager.get_health_summary()
        
        # Get all camera information
        cameras_info = manager.get_all_cameras_info()
        
        # Calculate processing statistics
        total_frames = sum(cam.frames_processed for cam in cameras_info)
        total_errors = sum(cam.errors_count for cam in cameras_info)
        error_rate = (total_errors / total_frames * 100) if total_frames > 0 else 0
        
        # Build statistics response
        stats = ServiceStats(
            service_name=settings.service_name,
            version=settings.service_version,
            start_time=manager.start_time,
            cameras=cameras_info,
            processing_stats={
                "total_frames_processed": total_frames,
                "total_errors": total_errors,
                "error_rate_percent": round(error_rate, 2),
                "active_streams": health_summary["active_streams"],
                "frames_per_second": 0  # Will be calculated when frame rate tracking is added
            },
            event_stats={
                "events_published": 0,  # Will be updated when event system is implemented
                "events_pending": 0,
                "events_failed": 0,
                "subscribers_connected": 0
            },
            performance_metrics={
                "memory_usage_mb": health_summary.get("memory_usage_mb", 0),
                "cpu_usage_percent": health_summary.get("cpu_usage_percent", 0),
                "uptime_seconds": health_summary["uptime_seconds"],
                "cameras_connected": health_summary["connected_cameras"],
                "cameras_total": health_summary["total_cameras"]
            }
        )
        
        return stats
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve service statistics: {str(e)}"
        )


# ===== PHASE 3: RECOGNITION INTEGRATION ENDPOINTS =====

@router.post("/{camera_id}/recognize")
async def process_frame_recognition(
    camera_id: str,
    confidence_threshold: float = 0.6,
    manager: CameraManager = Depends(get_camera_manager)
):
    """
    Process single frame for face recognition from camera
    PHASE 3: Real-time recognition integration with Service B
    """
    # Validate camera exists
    camera_info = manager.get_camera_info(camera_id)
    if camera_info is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Camera {camera_id} not found"
        )
    
    # Check if recognition service is available
    if not manager.recognition_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Recognition service not initialized"
        )
    
    try:
        # BYPASS QUEUE TIMEOUT - Capture frame directly for recognition
        camera = manager.cameras.get(camera_id)
        if not camera or not camera.cap:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Camera {camera_id} not accessible"
            )
        
        # Direct frame capture (bypasses queue timeout issue)
        ret, frame = camera.cap.read()
        if not ret or frame is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Failed to capture frame from camera {camera_id}"
            )
        
        # Create frame metadata
        import uuid
        from datetime import datetime
        from ..domain.models import FrameMetadata
        
        metadata = FrameMetadata(
            frame_id=str(uuid.uuid4()),
            camera_id=camera_id,
            timestamp=datetime.utcnow(),
            frame_number=1,  # Direct capture frame number
            width=frame.shape[1],
            height=frame.shape[0],
            channels=frame.shape[2] if len(frame.shape) > 2 else 1,
            file_size=frame.nbytes,  # Frame size in bytes
            quality_score=1.0  # Direct capture assumed good quality
        )
        
        # Process frame through recognition service
        recognition_result = await manager.recognition_service.process_frame_with_retry(
            frame, metadata, confidence_threshold=confidence_threshold
        )
        
        # Publish recognition event if event publisher is enabled
        if manager.event_publisher and recognition_result:
            try:
                await manager.event_publisher.publish_recognition_event(
                    camera_id=camera_id,
                    frame_id=metadata.frame_id,
                    persons_detected=recognition_result.persons_detected,
                    processing_time_ms=recognition_result.processing_time_ms,
                    confidence_threshold=recognition_result.confidence_threshold,
                    frame_metadata=metadata,
                    recognition_successful=recognition_result.success
                )
                logger.debug(f"Recognition event published for camera {camera_id}")
            except Exception as e:
                logger.error(f"Event publishing error for camera {camera_id}: {str(e)}")
        
        return {
            "camera_id": camera_id,
            "frame_id": metadata.frame_id,
            "timestamp": recognition_result.timestamp.isoformat(),
            "recognition_successful": recognition_result.success,
            "persons_detected": recognition_result.persons_detected,
            "processing_time_ms": recognition_result.processing_time_ms,
            "confidence_threshold": recognition_result.confidence_threshold,
            "frame_metadata": {
                "width": metadata.width,
                "height": metadata.height,
                "quality_score": getattr(metadata, 'quality_score', None),
                "quality_grade": getattr(metadata, 'quality_grade', {}).get('value', None) if hasattr(getattr(metadata, 'quality_grade', {}), 'value') else None
            },
            "error": recognition_result.error
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Recognition processing failed: {str(e)}"
        )


@router.get("/{camera_id}/recognition/status")
async def get_recognition_status(
    camera_id: str,
    manager: CameraManager = Depends(get_camera_manager)
):
    """
    Get recognition service status for specific camera
    Returns recognition performance metrics and health
    """
    # Validate camera exists
    camera_info = manager.get_camera_info(camera_id)
    if camera_info is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Camera {camera_id} not found"
        )
    
    try:
        # Check recognition service availability
        if not manager.recognition_service:
            return {
                "camera_id": camera_id,
                "recognition_enabled": False,
                "status": "disabled",
                "message": "Recognition service not initialized",
                "timestamp": datetime.utcnow().isoformat()
            }
        
        # Get recognition service health
        health_check = await manager.recognition_service.health_check()
        performance_stats = manager.recognition_service.get_performance_stats()
        
        return {
            "camera_id": camera_id,
            "recognition_enabled": True,
            "service_health": health_check,
            "performance_metrics": performance_stats,
            "camera_status": {
                "status": camera_info.status.value if hasattr(camera_info.status, 'value') else str(camera_info.status),
                "frames_processed": camera_info.frames_processed,
                "last_frame_time": camera_info.last_frame_time.isoformat() if camera_info.last_frame_time else None
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get recognition status: {str(e)}"
        )


@router.post("/recognition/test-integration")
async def test_recognition_integration(
    manager: CameraManager = Depends(get_camera_manager)
):
    """
    Test end-to-end recognition integration
    Processes frames from all available cameras through Service B
    """
    if not manager.recognition_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Recognition service not initialized"
        )
    
    try:
        # Test with all available cameras
        cameras_info = manager.get_all_cameras_info()
        if not cameras_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No cameras configured"
            )
        
        test_results = []
        
        for camera_info in cameras_info:
            camera_id = camera_info.camera_id
            
            try:
                # Get frame from camera
                frame_data = await manager.get_frame(camera_id, timeout=3.0)
                if frame_data is None:
                    test_results.append({
                        "camera_id": camera_id,
                        "success": False,
                        "error": "No frame available"
                    })
                    continue
                
                frame, metadata = frame_data
                
                # Test recognition
                recognition_result = await manager.recognition_service.process_frame(
                    frame, metadata, confidence_threshold=0.6
                )
                
                test_results.append({
                    "camera_id": camera_id,
                    "success": recognition_result.success,
                    "persons_detected": len(recognition_result.persons_detected),
                    "processing_time_ms": recognition_result.processing_time_ms,
                    "frame_quality": getattr(metadata, 'quality_score', None),
                    "error": recognition_result.error
                })
                
            except Exception as e:
                test_results.append({
                    "camera_id": camera_id,
                    "success": False,
                    "error": str(e)
                })
        
        # Calculate overall test results
        successful_tests = sum(1 for result in test_results if result.get("success", False))
        total_tests = len(test_results)
        
        return {
            "test_name": "End-to-End Recognition Integration Test",
            "timestamp": datetime.utcnow().isoformat(),
            "cameras_tested": total_tests,
            "successful_tests": successful_tests,
            "success_rate": (successful_tests / total_tests * 100) if total_tests > 0 else 0,
            "overall_success": successful_tests == total_tests,
            "detailed_results": test_results,
            "recognition_service_health": await manager.recognition_service.health_check()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Integration test failed: {str(e)}"
        )