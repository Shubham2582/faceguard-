"""
FACEGUARD V2 NOTIFICATION SERVICE - RECOGNITION WEBHOOK API
Rule 2: Zero Placeholder Code - Real webhook endpoints for recognition events  
Rule 3: Error-First Development - Comprehensive webhook validation and error handling

Webhook Integration: Receives person sighting events from recognition pipeline
"""

from fastapi import APIRouter, Depends, HTTPException, Header, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, Dict, Any
import structlog
import hmac
import hashlib
import json
from datetime import datetime
from decimal import Decimal

from storage.database import get_db_session
from services.alert_processor import get_alert_processor
from domain.schemas import SuccessResponse, ErrorResponse
from config.settings import get_settings

router = APIRouter(prefix="/webhook", tags=["recognition-webhook"])
logger = structlog.get_logger(__name__)
settings = get_settings()


@router.post("/recognition/sighting",
            response_model=SuccessResponse,
            status_code=202,
            summary="Receive person sighting event",
            description="Webhook endpoint to receive person sighting events from recognition service")
async def receive_sighting_webhook(
    sighting_data: Dict[str, Any],
    background_tasks: BackgroundTasks,
    x_faceguard_signature: Optional[str] = Header(None),
    x_faceguard_event: Optional[str] = Header(None),
    x_faceguard_timestamp: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Receive person sighting event from recognition service
    
    Expected payload:
    {
        "event_type": "person_sighting",
        "sighting_id": "uuid",
        "person_id": "uuid",
        "camera_id": "uuid", 
        "confidence_score": 0.95,
        "timestamp": "2024-01-20T10:30:00Z",
        "image_path": "/path/to/cropped/face.jpg",
        "metadata": {
            "face_quality": 0.9,
            "face_bbox": [100, 100, 200, 200],
            "processing_time_ms": 150
        }
    }
    """
    try:
        # Validate webhook signature if configured
        if settings.webhook_secret:
            if not x_faceguard_signature:
                raise HTTPException(
                    status_code=401,
                    detail=ErrorResponse(
                        error="missing_signature",
                        message="Webhook signature is required"
                    ).dict()
                )
            
            # Verify HMAC signature
            expected_signature = generate_webhook_signature(
                safe_json_dumps(sighting_data, sort_keys=True),
                settings.webhook_secret
            )
            
            if not hmac.compare_digest(x_faceguard_signature, expected_signature):
                await logger.awarn("Invalid webhook signature",
                                  provided=x_faceguard_signature[:20] + "...",
                                  expected=expected_signature[:20] + "...")
                raise HTTPException(
                    status_code=401,
                    detail=ErrorResponse(
                        error="invalid_signature",
                        message="Invalid webhook signature"
                    ).dict()
                )
        
        # Validate event type
        event_type = sighting_data.get("event_type")
        if event_type != "person_sighting":
            raise HTTPException(
                status_code=400,
                detail=ErrorResponse(
                    error="invalid_event_type",
                    message=f"Expected 'person_sighting' event, got '{event_type}'"
                ).dict()
            )
        
        # Validate required fields
        required_fields = ["sighting_id", "person_id", "camera_id", "confidence_score", "timestamp"]
        missing_fields = [field for field in required_fields if field not in sighting_data]
        
        if missing_fields:
            raise HTTPException(
                status_code=400,
                detail=ErrorResponse(
                    error="missing_fields",
                    message=f"Missing required fields: {missing_fields}"
                ).dict()
            )
        
        # Log webhook receipt
        await logger.ainfo("Person sighting webhook received",
                          sighting_id=sighting_data.get("sighting_id"),
                          person_id=sighting_data.get("person_id"),
                          camera_id=sighting_data.get("camera_id"),
                          confidence=sighting_data.get("confidence_score"))
        
        # Queue for background processing
        background_tasks.add_task(
            process_sighting_event,
            sighting_data
        )
        
        return SuccessResponse(
            message="Sighting event received and queued for processing",
            data={
                "sighting_id": sighting_data.get("sighting_id"),
                "queued_at": datetime.utcnow().isoformat(),
                "processing_status": "queued"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        await logger.aerror("Failed to process sighting webhook", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                error="webhook_processing_failed",
                message="Failed to process sighting webhook",
                details={"reason": str(e)}
            ).dict()
        )


@router.post("/recognition/batch",
            response_model=SuccessResponse,
            status_code=202,
            summary="Receive batch sighting events",
            description="Webhook endpoint to receive multiple person sighting events")
async def receive_batch_sighting_webhook(
    batch_data: Dict[str, Any],
    background_tasks: BackgroundTasks,
    x_faceguard_signature: Optional[str] = Header(None),
    x_faceguard_event: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Receive batch of person sighting events
    
    Expected payload:
    {
        "event_type": "batch_sighting",
        "batch_id": "uuid",
        "sightings": [
            {
                "sighting_id": "uuid",
                "person_id": "uuid",
                "camera_id": "uuid",
                "confidence_score": 0.95,
                "timestamp": "2024-01-20T10:30:00Z"
            },
            ...
        ]
    }
    """
    try:
        # Validate signature
        if settings.webhook_secret and x_faceguard_signature:
            expected_signature = generate_webhook_signature(
                safe_json_dumps(batch_data, sort_keys=True),
                settings.webhook_secret
            )
            
            if not hmac.compare_digest(x_faceguard_signature, expected_signature):
                raise HTTPException(
                    status_code=401,
                    detail=ErrorResponse(
                        error="invalid_signature",
                        message="Invalid webhook signature"
                    ).dict()
                )
        
        # Validate batch data
        if batch_data.get("event_type") != "batch_sighting":
            raise HTTPException(
                status_code=400,
                detail=ErrorResponse(
                    error="invalid_event_type",
                    message="Expected 'batch_sighting' event"
                ).dict()
            )
        
        sightings = batch_data.get("sightings", [])
        if not sightings:
            raise HTTPException(
                status_code=400,
                detail=ErrorResponse(
                    error="empty_batch",
                    message="Batch must contain at least one sighting"
                ).dict()
            )
        
        if len(sightings) > 100:  # Limit batch size
            raise HTTPException(
                status_code=400,
                detail=ErrorResponse(
                    error="batch_too_large",
                    message="Batch size limited to 100 sightings",
                    details={"provided": len(sightings), "max": 100}
                ).dict()
            )
        
        await logger.ainfo("Batch sighting webhook received",
                          batch_id=batch_data.get("batch_id"),
                          sighting_count=len(sightings))
        
        # Queue each sighting for processing
        for sighting in sightings:
            background_tasks.add_task(
                process_sighting_event,
                sighting
            )
        
        return SuccessResponse(
            message=f"Batch of {len(sightings)} sightings queued for processing",
            data={
                "batch_id": batch_data.get("batch_id"),
                "sighting_count": len(sightings),
                "queued_at": datetime.utcnow().isoformat()
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        await logger.aerror("Failed to process batch sighting webhook", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                error="batch_processing_failed",
                message="Failed to process batch sighting webhook",
                details={"reason": str(e)}
            ).dict()
        )


@router.post("/recognition/alert-status",
            response_model=SuccessResponse,
            summary="Update alert status from recognition service",
            description="Webhook to update alert status (acknowledge, resolve, etc.)")
async def update_alert_status_webhook(
    status_data: Dict[str, Any],
    x_faceguard_signature: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Update alert status from recognition service
    
    Expected payload:
    {
        "event_type": "alert_status_update",
        "alert_id": "uuid",
        "status": "acknowledged" | "resolved",
        "updated_by": "system | user_id",
        "reason": "optional reason for status change"
    }
    """
    try:
        # Validate signature if configured
        if settings.webhook_secret and x_faceguard_signature:
            expected_signature = generate_webhook_signature(
                safe_json_dumps(status_data, sort_keys=True),
                settings.webhook_secret
            )
            
            if not hmac.compare_digest(x_faceguard_signature, expected_signature):
                raise HTTPException(
                    status_code=401,
                    detail=ErrorResponse(
                        error="invalid_signature",
                        message="Invalid webhook signature"
                    ).dict()
                )
        
        alert_id = status_data.get("alert_id")
        status = status_data.get("status")
        updated_by = status_data.get("updated_by", "system")
        
        if not alert_id or not status:
            raise HTTPException(
                status_code=400,
                detail=ErrorResponse(
                    error="missing_fields",
                    message="alert_id and status are required"
                ).dict()
            )
        
        # Get alert processor
        alert_processor = await get_alert_processor()
        
        # Update alert status
        success = False
        if status == "acknowledged":
            success = await alert_processor.acknowledge_alert(alert_id, updated_by)
        elif status == "resolved":
            success = await alert_processor.resolve_alert(alert_id, updated_by)
        else:
            raise HTTPException(
                status_code=400,
                detail=ErrorResponse(
                    error="invalid_status",
                    message=f"Invalid status: {status}. Must be 'acknowledged' or 'resolved'"
                ).dict()
            )
        
        if success:
            await logger.ainfo("Alert status updated via webhook",
                              alert_id=alert_id,
                              status=status,
                              updated_by=updated_by)
            
            return SuccessResponse(
                message=f"Alert {alert_id} status updated to {status}",
                data={
                    "alert_id": alert_id,
                    "status": status,
                    "updated_at": datetime.utcnow().isoformat()
                }
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=ErrorResponse(
                    error="status_update_failed",
                    message="Failed to update alert status"
                ).dict()
            )
        
    except HTTPException:
        raise
    except Exception as e:
        await logger.aerror("Failed to update alert status", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                error="status_update_failed",
                message="Failed to update alert status",
                details={"reason": str(e)}
            ).dict()
        )


@router.get("/recognition/status",
           response_model=Dict[str, Any],
           summary="Get webhook integration status",
           description="Check the status of recognition webhook integration")
async def get_webhook_status():
    """Get webhook integration status and statistics"""
    try:
        # Get alert processor stats
        alert_processor = await get_alert_processor()
        processor_stats = await alert_processor.get_processing_stats()
        
        return {
            "status": "operational",
            "webhook_enabled": True,
            "signature_verification": bool(settings.webhook_secret),
            "supported_events": [
                "person_sighting",
                "batch_sighting",
                "alert_status_update"
            ],
            "processing_stats": processor_stats,
            "webhook_endpoints": {
                "sighting": "/webhook/recognition/sighting",
                "batch": "/webhook/recognition/batch",
                "status": "/webhook/recognition/alert-status"
            },
            "last_updated": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        await logger.aerror("Failed to get webhook status", error=str(e))
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


# Background processing functions
async def process_sighting_event(sighting_data: Dict[str, Any]):
    """
    Background task to process sighting event
    Rule 2: Zero Placeholder Code - Real alert processing
    """
    try:
        await logger.ainfo("Processing sighting event",
                          sighting_id=sighting_data.get("sighting_id"))
        
        # Get alert processor
        alert_processor = await get_alert_processor()
        
        # Process the sighting
        result = await alert_processor.process_person_sighting(sighting_data)
        
        if result["status"] == "processed":
            await logger.ainfo("Sighting processed successfully",
                              sighting_id=sighting_data.get("sighting_id"),
                              alerts_triggered=result.get("alerts_triggered", 0))
        else:
            await logger.aerror("Sighting processing failed",
                               sighting_id=sighting_data.get("sighting_id"),
                               error=result.get("error"))
        
    except Exception as e:
        await logger.aerror("Failed to process sighting event",
                           sighting_id=sighting_data.get("sighting_id"),
                           error=str(e))


def safe_json_dumps(data: Any, sort_keys: bool = True) -> str:
    """
    Safe JSON serialization that handles datetime and decimal objects
    Rule 3: Error-First Development - Handle serialization edge cases
    """
    def json_serializer(obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, Decimal):
            return float(obj)
        elif hasattr(obj, 'isoformat'):  # Handle other datetime-like objects
            return obj.isoformat()
        elif hasattr(obj, '__dict__'):  # Handle object instances
            return obj.__dict__
        else:
            raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
    
    return json.dumps(data, sort_keys=sort_keys, default=json_serializer)


def generate_webhook_signature(payload: str, secret: str) -> str:
    """Generate HMAC signature for webhook verification"""
    signature = hmac.new(
        secret.encode('utf-8'),
        payload.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    return f"sha256={signature}"


# Webhook registration helper
async def register_webhook_with_recognition_service():
    """
    Register this webhook endpoint with the face-recognition-service
    This would be called during service initialization
    """
    try:
        import aiohttp
        
        webhook_config = {
            "service_name": "notification-service",
            "webhook_url": f"{settings.notification_service_url}/webhook/recognition/sighting",
            "batch_url": f"{settings.notification_service_url}/webhook/recognition/batch",
            "events": ["person_sighting", "batch_sighting"],
            "active": True,
            "secret": settings.webhook_secret if settings.webhook_secret else None
        }
        
        # Register with recognition service
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{settings.face_recognition_service_url}/webhooks/register",
                json=webhook_config
            ) as response:
                if response.status == 200:
                    await logger.ainfo("Webhook registered with recognition service")
                else:
                    await logger.aerror("Failed to register webhook",
                                       status=response.status)
        
    except Exception as e:
        await logger.aerror("Webhook registration failed", error=str(e))