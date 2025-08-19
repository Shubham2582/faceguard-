"""
FACEGUARD V2 CORE DATA SERVICE - PERSON SIGHTINGS API
Rule 2: Zero Placeholder Code - Real REST API endpoints
Rule 3: Error-First Development - Proper HTTP status codes
Performance: Async non-blocking sighting recording
"""

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from datetime import datetime, timedelta
import structlog
import asyncio
import cv2
import numpy as np

from storage.database import get_db_session
from services.sighting_service import SightingService
from domain.schemas import (
    SightingCreate, SightingResponse, SightingListResponse,
    SightingAnalytics, SuccessResponse, ErrorResponse
)
from utils.image_storage import storage_manager

logger = structlog.get_logger(__name__)
router = APIRouter(prefix="/sightings", tags=["sightings"])


@router.post("/", response_model=SightingResponse, status_code=201)
async def create_sighting(
    sighting_data: SightingCreate,
    session: AsyncSession = Depends(get_db_session)
) -> SightingResponse:
    """
    Record new person sighting
    Rule 2: Zero Placeholder Code - Real async sighting recording
    Rule 3: Error-First Development - Comprehensive validation
    
    This endpoint is designed for async background recording to not impact
    recognition pipeline performance.
    
    Returns:
        SightingResponse: Created sighting data
        
    HTTP Status Codes:
        201: Sighting created successfully
        400: Validation error or invalid person/camera
        500: Internal server error
    """
    try:
        await logger.ainfo("Recording new sighting", 
                           person_id=sighting_data.person_id,
                           camera_id=sighting_data.camera_id,
                           source_type=sighting_data.source_type)
        
        sighting_service = SightingService(session)
        sighting = await sighting_service.create_sighting(sighting_data)
        
        await logger.ainfo("Sighting recorded successfully", 
                           sighting_id=sighting.id,
                           person_id=sighting.person_id)
        return sighting
        
    except ValueError as e:
        await logger.awarn("Sighting validation failed", error=str(e))
        raise HTTPException(status_code=400, detail={
            "error": "validation_error",
            "message": str(e)
        })
    except Exception as e:
        await logger.aerror("Sighting creation failed", error=str(e))
        raise HTTPException(status_code=500, detail={
            "error": "internal_error", 
            "message": "Failed to record sighting"
        })


@router.post("/with-image", response_model=SightingResponse, status_code=201)
async def create_sighting_with_image(
    person_id: str,
    camera_id: str,
    confidence_score: float,
    source_type: str = "camera_stream",
    face_bbox: Optional[str] = None,  # JSON string "[x1,y1,x2,y2]"
    image: UploadFile = File(...),
    session: AsyncSession = Depends(get_db_session)
) -> SightingResponse:
    """
    Record sighting with face image for storage and quality assessment
    
    This endpoint handles complete sighting workflow:
    1. Validate sighting data
    2. Process and store face image
    3. Assess image quality
    4. Record sighting in database
    5. Determine if embeddings should be updated
    
    Returns:
        SightingResponse: Created sighting with image metadata
    """
    try:
        await logger.ainfo("Recording sighting with image", 
                           person_id=person_id,
                           camera_id=camera_id,
                           source_type=source_type)
        
        # 1. Validate image format
        if not image.content_type.startswith('image/'):
            raise ValueError("Invalid image format")
        
        # 2. Read and process image
        image_bytes = await image.read()
        nparr = np.frombuffer(image_bytes, np.uint8)
        cv_image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if cv_image is None:
            raise ValueError("Failed to decode image")
        
        # 3. Save image with compression and quality assessment
        file_path, quality_score, metadata = await storage_manager.save_sighting_image(
            image=cv_image,
            person_id=person_id,
            camera_id=camera_id,
            source_type=source_type
        )
        
        # 4. Create sighting record
        sighting_service = SightingService(session)
        
        # Parse face_bbox if provided
        bbox_data = None
        if face_bbox:
            try:
                import json
                bbox_data = json.loads(face_bbox)
            except:
                bbox_data = None
        
        sighting_create = SightingCreate(
            person_id=person_id,
            camera_id=camera_id,
            confidence_score=confidence_score,
            source_type=source_type,
            source_metadata=metadata,
            cropped_image_path=file_path,
            image_quality_score=quality_score,
            face_bbox=bbox_data
        )
        
        sighting = await sighting_service.create_sighting(sighting_create)
        
        # 5. Check if embeddings should be updated (async background task)
        should_update = await storage_manager.should_update_embeddings(
            quality_score, person_id
        )
        
        if should_update:
            # Schedule embedding update in background
            asyncio.create_task(
                sighting_service.schedule_embedding_update(sighting.id)
            )
            await logger.ainfo("Embedding update scheduled", 
                               sighting_id=sighting.id,
                               quality_score=quality_score)
        
        await logger.ainfo("Sighting with image recorded successfully", 
                           sighting_id=sighting.id,
                           file_path=file_path,
                           quality_score=quality_score,
                           embedding_update=should_update)
        
        return sighting
        
    except ValueError as e:
        await logger.awarn("Sighting with image validation failed", error=str(e))
        raise HTTPException(status_code=400, detail={
            "error": "validation_error",
            "message": str(e)
        })
    except Exception as e:
        await logger.aerror("Sighting with image creation failed", error=str(e))
        raise HTTPException(status_code=500, detail={
            "error": "internal_error",
            "message": "Failed to record sighting with image"
        })


@router.get("/person/{person_id}", response_model=SightingListResponse)
async def get_person_sightings(
    person_id: str,
    days: int = Query(default=30, ge=1, le=365, description="Days of history"),
    page: int = Query(default=1, ge=1, description="Page number"),
    limit: int = Query(default=20, ge=1, le=100, description="Items per page"),
    source_type: Optional[str] = Query(default=None, description="Filter by source type"),
    session: AsyncSession = Depends(get_db_session)
) -> SightingListResponse:
    """
    Get person sighting history with pagination
    
    Optimized query with temporal filtering for performance.
    Uses indexed queries to ensure fast response times.
    
    Returns:
        SightingListResponse: Paginated sighting history
    """
    try:
        await logger.ainfo("Retrieving person sightings", 
                           person_id=person_id,
                           days=days,
                           page=page,
                           limit=limit)
        
        sighting_service = SightingService(session)
        sightings = await sighting_service.get_person_sightings(
            person_id=person_id,
            days=days,
            page=page,
            limit=limit,
            source_type=source_type
        )
        
        await logger.ainfo("Person sightings retrieved successfully",
                           person_id=person_id,
                           total=sightings.total,
                           returned=len(sightings.sightings))
        return sightings
        
    except ValueError as e:
        await logger.awarn("Person sightings validation failed", error=str(e))
        raise HTTPException(status_code=400, detail={
            "error": "validation_error",
            "message": str(e)
        })
    except Exception as e:
        await logger.aerror("Person sightings retrieval failed", error=str(e))
        raise HTTPException(status_code=500, detail={
            "error": "internal_error",
            "message": "Failed to retrieve person sightings"
        })


@router.get("/camera/{camera_id}", response_model=SightingListResponse)
async def get_camera_sightings(
    camera_id: str,
    days: int = Query(default=7, ge=1, le=90, description="Days of history"),
    page: int = Query(default=1, ge=1, description="Page number"),
    limit: int = Query(default=50, ge=1, le=200, description="Items per page"),
    session: AsyncSession = Depends(get_db_session)
) -> SightingListResponse:
    """
    Get camera sighting activity with pagination
    
    Optimized for camera monitoring dashboards.
    Limited to 90 days to ensure performance.
    
    Returns:
        SightingListResponse: Paginated camera sightings
    """
    try:
        await logger.ainfo("Retrieving camera sightings", 
                           camera_id=camera_id,
                           days=days,
                           page=page,
                           limit=limit)
        
        sighting_service = SightingService(session)
        sightings = await sighting_service.get_camera_sightings(
            camera_id=camera_id,
            days=days,
            page=page,
            limit=limit
        )
        
        await logger.ainfo("Camera sightings retrieved successfully",
                           camera_id=camera_id,
                           total=sightings.total,
                           returned=len(sightings.sightings))
        return sightings
        
    except ValueError as e:
        await logger.awarn("Camera sightings validation failed", error=str(e))
        raise HTTPException(status_code=400, detail={
            "error": "validation_error",
            "message": str(e)
        })
    except Exception as e:
        await logger.aerror("Camera sightings retrieval failed", error=str(e))
        raise HTTPException(status_code=500, detail={
            "error": "internal_error",
            "message": "Failed to retrieve camera sightings"
        })


@router.get("/analytics/summary", response_model=SightingAnalytics)
async def get_sighting_analytics(
    days: int = Query(default=7, ge=1, le=30, description="Days to analyze"),
    session: AsyncSession = Depends(get_db_session)
) -> SightingAnalytics:
    """
    Get sighting analytics for dashboard
    
    Aggregated statistics optimized for dashboard display.
    Limited to 30 days for performance.
    
    Returns:
        SightingAnalytics: Aggregated sighting statistics
    """
    try:
        await logger.ainfo("Generating sighting analytics", days=days)
        
        sighting_service = SightingService(session)
        analytics = await sighting_service.get_sighting_analytics(days)
        
        await logger.ainfo("Sighting analytics generated successfully",
                           total_sightings=analytics.total_sightings,
                           unique_persons=analytics.unique_persons,
                           active_cameras=analytics.active_cameras)
        return analytics
        
    except Exception as e:
        await logger.aerror("Sighting analytics generation failed", error=str(e))
        raise HTTPException(status_code=500, detail={
            "error": "internal_error",
            "message": "Failed to generate sighting analytics"
        })


@router.get("/recent", response_model=List[SightingResponse])
async def get_recent_sightings(
    limit: int = Query(default=10, ge=1, le=50, description="Number of recent sightings"),
    hours: int = Query(default=24, ge=1, le=168, description="Hours of history"),
    session: AsyncSession = Depends(get_db_session)
) -> List[SightingResponse]:
    """
    Get most recent sightings across all cameras
    
    Optimized for real-time dashboard displays.
    Limited to 1 week (168 hours) for performance.
    
    Returns:
        List[SightingResponse]: Recent sightings ordered by timestamp
    """
    try:
        await logger.ainfo("Retrieving recent sightings", 
                           limit=limit,
                           hours=hours)
        
        sighting_service = SightingService(session)
        sightings = await sighting_service.get_recent_sightings(
            limit=limit,
            hours=hours
        )
        
        await logger.ainfo("Recent sightings retrieved successfully",
                           returned=len(sightings))
        return sightings
        
    except Exception as e:
        await logger.aerror("Recent sightings retrieval failed", error=str(e))
        raise HTTPException(status_code=500, detail={
            "error": "internal_error",
            "message": "Failed to retrieve recent sightings"
        })


@router.delete("/cleanup", response_model=SuccessResponse)
async def cleanup_old_sightings(
    days_to_keep: int = Query(default=90, ge=30, le=365, description="Days to retain"),
    session: AsyncSession = Depends(get_db_session)
) -> SuccessResponse:
    """
    Clean up old sighting records and images
    
    Maintenance endpoint for storage management.
    Requires admin privileges in production.
    
    Returns:
        SuccessResponse: Cleanup statistics
    """
    try:
        await logger.ainfo("Starting sighting cleanup", days_to_keep=days_to_keep)
        
        sighting_service = SightingService(session)
        result = await sighting_service.cleanup_old_sightings(days_to_keep)
        
        await logger.ainfo("Sighting cleanup completed successfully",
                           **result)
        
        return SuccessResponse(
            message=f"Cleanup completed: {result['deleted_records']} records, {result['deleted_files']} files",
            data=result
        )
        
    except Exception as e:
        await logger.aerror("Sighting cleanup failed", error=str(e))
        raise HTTPException(status_code=500, detail={
            "error": "internal_error",
            "message": "Failed to cleanup old sightings"
        })


@router.get("/storage/stats", response_model=dict)
async def get_storage_statistics(
    session: AsyncSession = Depends(get_db_session)
) -> dict:
    """
    Get sighting storage statistics
    
    Returns storage usage, file counts, and performance metrics.
    
    Returns:
        dict: Storage statistics and metrics
    """
    try:
        await logger.ainfo("Retrieving storage statistics")
        
        # Get storage manager statistics
        storage_stats = storage_manager.get_storage_stats()
        
        # Get database statistics
        sighting_service = SightingService(session)
        db_stats = await sighting_service.get_storage_statistics()
        
        combined_stats = {
            "storage": storage_stats,
            "database": db_stats,
            "timestamp": datetime.now().isoformat()
        }
        
        await logger.ainfo("Storage statistics retrieved successfully")
        return combined_stats
        
    except Exception as e:
        await logger.aerror("Storage statistics retrieval failed", error=str(e))
        raise HTTPException(status_code=500, detail={
            "error": "internal_error",
            "message": "Failed to retrieve storage statistics"
        })