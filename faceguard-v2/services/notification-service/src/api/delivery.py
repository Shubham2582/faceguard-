"""
FACEGUARD V2 NOTIFICATION SERVICE - DELIVERY API (REDESIGNED)
CRITICAL: Uses Core Data Service API - NO direct database access
Rule 1: Incremental Completeness - 100% functional implementation
Rule 2: Zero Placeholder Code - Real notification delivery via Core Data Service
Rule 3: Error-First Development - Comprehensive validation and error handling
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict, Any
import structlog
from datetime import datetime
from uuid import UUID, uuid4

from clients.core_data_client import get_core_data_client, CoreDataServiceError
from pydantic import BaseModel


# Delivery request schema for API requests
class SimpleDeliveryRequest(BaseModel):
    subject: str
    message: str
    recipient: str
    channel_ids: List[str]
    priority: str = "medium"  # low, medium, high
    delivery_options: Dict[str, Any] = {}


router = APIRouter(prefix="/delivery", tags=["delivery"])
logger = structlog.get_logger(__name__)


@router.post("/send", status_code=201)
async def send_notification(delivery_request: SimpleDeliveryRequest):
    """
    Send notification - REDESIGNED to use Core Data Service API
    """
    try:
        # Rule 3: Error-First Development - Validate input data
        if not delivery_request.subject.strip():
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "validation_error",
                    "message": "Subject cannot be empty"
                }
            )
        
        if not delivery_request.message.strip():
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "validation_error",
                    "message": "Message cannot be empty"
                }
            )
        
        if not delivery_request.recipient.strip():
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "validation_error",
                    "message": "Recipient cannot be empty"
                }
            )
        
        if not delivery_request.channel_ids:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "validation_error",
                    "message": "At least one channel ID is required"
                }
            )
        
        # Validate priority
        valid_priorities = ["low", "medium", "high"]
        if delivery_request.priority not in valid_priorities:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "validation_error",
                    "message": f"Priority must be one of: {', '.join(valid_priorities)}"
                }
            )
        
        # Validate channel IDs are valid UUIDs
        try:
            uuid_channel_ids = [str(UUID(cid)) for cid in delivery_request.channel_ids]
        except (ValueError, TypeError) as e:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "validation_error",
                    "message": f"Invalid channel ID format: {str(e)}"
                }
            )
        
        # Get Core Data Service client
        client = await get_core_data_client()
        
        # Validate channels exist via Core Data Service
        try:
            channels = await client.get_notification_channels()
            
            # Check if requested channels exist and are active
            channel_dict = {ch["id"]: ch for ch in channels}
            missing_channels = []
            inactive_channels = []
            
            for channel_id in uuid_channel_ids:
                if channel_id not in channel_dict:
                    missing_channels.append(channel_id)
                elif not channel_dict[channel_id].get("is_active", False):
                    inactive_channels.append(channel_dict[channel_id].get("channel_name", channel_id))
            
            if missing_channels:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error": "invalid_channels",
                        "message": f"Notification channels not found: {missing_channels}"
                    }
                )
            
            if inactive_channels:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error": "inactive_channels",
                        "message": f"Some channels are inactive: {inactive_channels}"
                    }
                )
        
        except CoreDataServiceError as e:
            await logger.aerror(
                "Failed to validate channels via Core Data Service",
                error=str(e),
                status_code=e.status_code
            )
            # Continue with delivery despite validation failure
            # This allows graceful degradation
            await logger.awarn("Proceeding with delivery despite channel validation failure")
        
        # Prepare delivery data for Core Data Service
        delivery_id = str(uuid4())
        delivery_data = {
            "delivery_id": delivery_id,
            "subject": delivery_request.subject,
            "message": delivery_request.message,
            "recipient": delivery_request.recipient,
            "channel_ids": uuid_channel_ids,
            "priority": delivery_request.priority,
            "delivery_options": delivery_request.delivery_options,
            "status": "pending"
        }
        
        # Send delivery request to Core Data Service notification logs endpoint
        try:
            result = await client._make_request(
                "POST",
                "/notifications/logs",
                json=delivery_data
            )
            
            await logger.ainfo(
                "Notification delivery queued via Core Data Service",
                delivery_id=delivery_id,
                recipient=delivery_request.recipient,
                channels=len(delivery_request.channel_ids),
                log_id=result.get("id")
            )
            
            return {
                "delivery_id": delivery_id,
                "status": "pending",
                "message": "Notification queued for delivery via Core Data Service",
                "recipient": delivery_request.recipient,
                "subject": delivery_request.subject,
                "channels_targeted": len(delivery_request.channel_ids),
                "priority": delivery_request.priority,
                "log_id": result.get("id"),
                "created_at": result.get("created_at", datetime.utcnow().isoformat())
            }
        
        except CoreDataServiceError as e:
            await logger.aerror(
                "Core Data Service error while queuing notification",
                error=str(e),
                status_code=e.status_code,
                delivery_id=delivery_id
            )
            raise HTTPException(
                status_code=e.status_code or 503,
                detail={
                    "error": "core_data_service_error",
                    "message": f"Failed to queue notification via Core Data Service: {e.message}",
                    "details": e.details
                }
            )
        
    except HTTPException:
        raise
    except Exception as e:
        await logger.aerror("Failed to queue notification delivery", error=str(e))
        raise HTTPException(
            status_code=500,
            detail={
                "error": "delivery_failed",
                "message": "Failed to queue notification for delivery",
                "details": {"reason": str(e)}
            }
        )


@router.get("/logs")
async def list_delivery_logs(
    page: int = Query(1, ge=1, description="Page number starting from 1"),
    limit: int = Query(50, ge=1, le=100, description="Number of logs per page"),
    status: Optional[str] = Query(None, description="Filter by delivery status"),
    recipient: Optional[str] = Query(None, description="Filter by recipient")
):
    """
    List delivery logs - REDESIGNED to use Core Data Service API
    """
    try:
        # Get Core Data Service client
        client = await get_core_data_client()
        
        # Build filters for Core Data Service
        filters = {}
        if status:
            filters["status"] = status
        if recipient:
            filters["recipient"] = recipient
        
        # Get notification logs from Core Data Service
        result = await client.get_notification_logs(page=page, limit=limit, **filters)
        
        await logger.ainfo(
            "Retrieved delivery logs from Core Data Service",
            page=page,
            limit=limit,
            total=result.get("total", 0),
            filters=filters
        )
        
        return {
            "logs": result.get("logs", []),
            "total": result.get("total", 0),
            "page": page,
            "limit": limit,
            "pages": (result.get("total", 0) + limit - 1) // limit if result.get("total", 0) > 0 else 0
        }
        
    except CoreDataServiceError as e:
        await logger.aerror(
            "Core Data Service error while listing delivery logs",
            error=str(e),
            status_code=e.status_code
        )
        raise HTTPException(
            status_code=e.status_code or 503,
            detail={
                "error": "core_data_service_error",
                "message": f"Failed to retrieve delivery logs from Core Data Service: {e.message}",
                "details": e.details
            }
        )
    except Exception as e:
        await logger.aerror("Failed to list delivery logs", error=str(e))
        raise HTTPException(
            status_code=500,
            detail={
                "error": "service_error",
                "message": "Failed to retrieve delivery logs",
                "details": {"reason": str(e)}
            }
        )


@router.get("/{delivery_id}/status")
async def get_delivery_status(delivery_id: str):
    """
    Get delivery status - REDESIGNED to use Core Data Service API
    """
    try:
        # Rule 3: Error-First Development - Validate UUID format
        try:
            UUID(delivery_id)  # This will raise ValueError if invalid UUID
        except (ValueError, TypeError):
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "delivery_not_found",
                    "message": f"Delivery with ID {delivery_id} not found"
                }
            )
        
        # Get Core Data Service client
        client = await get_core_data_client()
        
        # Get delivery status from Core Data Service notification logs
        try:
            # Search logs by delivery_id filter
            result = await client.get_notification_logs(delivery_id=delivery_id, limit=1)
            logs = result.get("logs", [])
            
            if not logs:
                raise HTTPException(
                    status_code=404,
                    detail={
                        "error": "delivery_not_found",
                        "message": f"Delivery with ID {delivery_id} not found"
                    }
                )
            
            log_entry = logs[0]
            
            await logger.ainfo(
                "Retrieved delivery status from Core Data Service",
                delivery_id=delivery_id,
                status=log_entry.get("status")
            )
            
            return {
                "delivery_id": delivery_id,
                "log_id": log_entry.get("id"),
                "status": log_entry.get("status", "unknown"),
                "subject": log_entry.get("subject", "Unknown"),
                "message": log_entry.get("message", "Unknown"),
                "recipient": log_entry.get("recipient", "Unknown"),
                "priority": log_entry.get("priority", "Unknown"),
                "channels_count": log_entry.get("channels_count", 0),
                "sent_at": log_entry.get("sent_at"),
                "delivered_at": log_entry.get("delivered_at"),
                "error_message": log_entry.get("error_message"),
                "created_at": log_entry.get("created_at"),
                "updated_at": log_entry.get("updated_at")
            }
        
        except CoreDataServiceError as e:
            await logger.aerror(
                "Core Data Service error while getting delivery status",
                error=str(e),
                status_code=e.status_code,
                delivery_id=delivery_id
            )
            
            # Handle 404 specifically
            if e.status_code == 404:
                raise HTTPException(
                    status_code=404,
                    detail={
                        "error": "delivery_not_found",
                        "message": f"Delivery with ID {delivery_id} not found"
                    }
                )
            
            raise HTTPException(
                status_code=e.status_code or 503,
                detail={
                    "error": "core_data_service_error",
                    "message": f"Failed to retrieve delivery status from Core Data Service: {e.message}",
                    "details": e.details
                }
            )
        
    except HTTPException:
        raise
    except Exception as e:
        await logger.aerror("Failed to get delivery status", delivery_id=delivery_id, error=str(e))
        raise HTTPException(
            status_code=500,
            detail={
                "error": "service_error",
                "message": "Failed to retrieve delivery status",
                "details": {"delivery_id": delivery_id, "reason": str(e)}
            }
        )


@router.post("/test")
async def test_delivery_system():
    """
    Test delivery system - REDESIGNED to use Core Data Service API
    """
    try:
        # Get Core Data Service client
        client = await get_core_data_client()
        
        # Test Core Data Service connectivity
        health_status = await client.health_check()
        
        # Test channels endpoint
        try:
            channels = await client.get_notification_channels()
            channels_status = {"status": "healthy", "count": len(channels)}
        except CoreDataServiceError:
            channels_status = {"status": "error", "message": "Failed to retrieve channels"}
        
        # Test notification logs endpoint
        try:
            logs = await client.get_notification_logs(limit=1)
            logs_status = {"status": "healthy", "count": logs.get("total", 0)}
        except CoreDataServiceError:
            logs_status = {"status": "error", "message": "Failed to retrieve logs"}
        
        overall_status = "healthy"
        if health_status.get("status") != "healthy":
            overall_status = "unhealthy"
        elif channels_status.get("status") != "healthy" or logs_status.get("status") != "healthy":
            overall_status = "degraded"
        
        return {
            "status": overall_status,
            "architecture": "HTTP_CLIENT_ONLY",
            "timestamp": datetime.utcnow().isoformat(),
            "components": {
                "core_data_service": health_status,
                "notification_channels": channels_status,
                "notification_logs": logs_status
            },
            "delivery_capabilities": {
                "can_queue_notifications": overall_status in ["healthy", "degraded"],
                "can_track_status": logs_status.get("status") == "healthy",
                "can_validate_channels": channels_status.get("status") == "healthy"
            }
        }
        
    except Exception as e:
        await logger.aerror("Delivery system test failed", error=str(e))
        return {
            "status": "unhealthy",
            "architecture": "HTTP_CLIENT_ONLY",
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e),
            "delivery_capabilities": {
                "can_queue_notifications": False,
                "can_track_status": False,
                "can_validate_channels": False
            }
        }