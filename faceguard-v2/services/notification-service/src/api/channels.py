"""
FACEGUARD V2 NOTIFICATION SERVICE - CHANNELS API (REDESIGNED)
CRITICAL: Uses Core Data Service API - NO direct database access
Rule 1: Incremental Completeness - 100% functional implementation
Rule 2: Zero Placeholder Code - Real notification channel management via Core Data Service
Rule 3: Error-First Development - Comprehensive validation and error handling
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict, Any
import structlog
from datetime import datetime
from uuid import UUID

from clients.core_data_client import get_core_data_client, CoreDataServiceError
from pydantic import BaseModel


# Channel creation schema for API requests
class SimpleChannelCreate(BaseModel):
    channel_name: str
    channel_type: str
    configuration: Dict[str, Any]
    is_active: bool = True
    rate_limit_per_minute: int = 100
    retry_attempts: int = 3
    timeout_seconds: int = 30


router = APIRouter(prefix="/channels", tags=["channels"])
logger = structlog.get_logger(__name__)


@router.get("")
async def list_notification_channels(
    page: int = Query(1, ge=1, description="Page number starting from 1"),
    limit: int = Query(50, ge=1, le=100, description="Number of channels per page"),
    channel_type: Optional[str] = Query(None, description="Filter by channel type"),
    active_only: Optional[bool] = Query(None, description="Filter by active status"),
    search: Optional[str] = Query(None, description="Search in channel name")
):
    """
    List notification channels - REDESIGNED to use Core Data Service API
    """
    try:
        # Get Core Data Service client
        client = await get_core_data_client()
        
        # Get channels from Core Data Service
        channels = await client.get_notification_channels()
        
        await logger.ainfo(
            "Retrieved channels from Core Data Service",
            total_channels=len(channels),
            page=page,
            limit=limit
        )
        
        # Apply filters
        filtered_channels = channels
        
        if channel_type:
            filtered_channels = [ch for ch in filtered_channels if ch.get("channel_type") == channel_type]
        
        if active_only is not None:
            filtered_channels = [ch for ch in filtered_channels if ch.get("is_active") == active_only]
        
        if search:
            search_lower = search.lower()
            filtered_channels = [
                ch for ch in filtered_channels 
                if search_lower in ch.get("channel_name", "").lower()
            ]
        
        # Apply pagination
        total = len(filtered_channels)
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        paginated_channels = filtered_channels[start_idx:end_idx]
        
        return {
            "channels": paginated_channels,
            "total": total,
            "page": page,
            "limit": limit,
            "pages": (total + limit - 1) // limit if total > 0 else 0
        }
        
    except CoreDataServiceError as e:
        await logger.aerror(
            "Core Data Service error while listing channels",
            error=str(e),
            status_code=e.status_code
        )
        raise HTTPException(
            status_code=e.status_code or 503,
            detail={
                "error": "core_data_service_error",
                "message": f"Failed to retrieve channels from Core Data Service: {e.message}",
                "details": e.details
            }
        )
    except Exception as e:
        await logger.aerror("Failed to list notification channels", error=str(e))
        raise HTTPException(
            status_code=500,
            detail={
                "error": "service_error",
                "message": "Failed to retrieve notification channels",
                "details": {"reason": str(e)}
            }
        )


@router.post("", status_code=201)
async def create_notification_channel(channel_data: SimpleChannelCreate):
    """
    Create new notification channel - REDESIGNED to use Core Data Service API
    """
    try:
        # Rule 3: Error-First Development - Validate configuration
        if channel_data.channel_type == "email":
            if "email_address" not in channel_data.configuration:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error": "validation_error",
                        "message": "Email channel requires email_address in configuration"
                    }
                )
        elif channel_data.channel_type == "webhook":
            if "url" not in channel_data.configuration:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error": "validation_error",
                        "message": "Webhook channel requires url in configuration"
                    }
                )
        elif channel_data.channel_type == "sms":
            if "phone_number" not in channel_data.configuration:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error": "validation_error",
                        "message": "SMS channel requires phone_number in configuration"
                    }
                )
        
        # Get Core Data Service client
        client = await get_core_data_client()
        
        # Create channel via Core Data Service
        channel_dict = channel_data.model_dump()
        result = await client.create_notification_channel(channel_dict)
        
        await logger.ainfo(
            "Notification channel created via Core Data Service",
            channel_id=result.get("id"),
            channel_name=channel_data.channel_name,
            channel_type=channel_data.channel_type
        )
        
        return result
        
    except CoreDataServiceError as e:
        await logger.aerror(
            "Core Data Service error while creating channel",
            error=str(e),
            status_code=e.status_code,
            channel_name=channel_data.channel_name
        )
        
        # Handle specific error codes
        if e.status_code == 409:
            raise HTTPException(
                status_code=409,
                detail={
                    "error": "channel_name_exists",
                    "message": f"Channel name '{channel_data.channel_name}' already exists"
                }
            )
        
        raise HTTPException(
            status_code=e.status_code or 503,
            detail={
                "error": "core_data_service_error",
                "message": f"Failed to create channel via Core Data Service: {e.message}",
                "details": e.details
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        await logger.aerror("Failed to create notification channel", error=str(e))
        raise HTTPException(
            status_code=500,
            detail={
                "error": "creation_failed",
                "message": "Failed to create notification channel",
                "details": {"reason": str(e)}
            }
        )


@router.get("/{channel_id}")
async def get_notification_channel(channel_id: str):
    """
    Get notification channel by ID - REDESIGNED to use Core Data Service API
    """
    try:
        # Rule 3: Error-First Development - Validate UUID format
        try:
            UUID(channel_id)  # This will raise ValueError if invalid UUID
        except (ValueError, TypeError):
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "channel_not_found",
                    "message": f"Notification channel with ID {channel_id} not found"
                }
            )
        
        # Get Core Data Service client
        client = await get_core_data_client()
        
        # Get channel from Core Data Service
        result = await client.get_notification_channel(channel_id)
        
        await logger.ainfo(
            "Retrieved channel from Core Data Service",
            channel_id=channel_id,
            channel_name=result.get("channel_name")
        )
        
        return result
        
    except CoreDataServiceError as e:
        await logger.aerror(
            "Core Data Service error while getting channel",
            error=str(e),
            status_code=e.status_code,
            channel_id=channel_id
        )
        
        # Handle 404 specifically
        if e.status_code == 404:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "channel_not_found",
                    "message": f"Notification channel with ID {channel_id} not found"
                }
            )
        
        raise HTTPException(
            status_code=e.status_code or 503,
            detail={
                "error": "core_data_service_error",
                "message": f"Failed to retrieve channel from Core Data Service: {e.message}",
                "details": e.details
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        await logger.aerror("Failed to get notification channel", channel_id=channel_id, error=str(e))
        raise HTTPException(
            status_code=500,
            detail={
                "error": "service_error",
                "message": "Failed to retrieve notification channel",
                "details": {"channel_id": channel_id, "reason": str(e)}
            }
        )


@router.put("/{channel_id}")
async def update_notification_channel(channel_id: str, channel_data: SimpleChannelCreate):
    """
    Update notification channel - REDESIGNED to use Core Data Service API
    """
    try:
        # Rule 3: Error-First Development - Validate configuration
        if channel_data.channel_type == "email":
            if "email_address" not in channel_data.configuration:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error": "validation_error",
                        "message": "Email channel requires email_address in configuration"
                    }
                )
        elif channel_data.channel_type == "webhook":
            if "url" not in channel_data.configuration:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error": "validation_error",
                        "message": "Webhook channel requires url in configuration"
                    }
                )
        elif channel_data.channel_type == "sms":
            if "phone_number" not in channel_data.configuration:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error": "validation_error",
                        "message": "SMS channel requires phone_number in configuration"
                    }
                )
        
        # Get Core Data Service client
        client = await get_core_data_client()
        
        # Update channel via Core Data Service
        channel_dict = channel_data.model_dump()
        result = await client.update_notification_channel(channel_id, channel_dict)
        
        await logger.ainfo(
            "Notification channel updated via Core Data Service",
            channel_id=channel_id,
            channel_name=channel_data.channel_name
        )
        
        return result
        
    except CoreDataServiceError as e:
        await logger.aerror(
            "Core Data Service error while updating channel",
            error=str(e),
            status_code=e.status_code,
            channel_id=channel_id
        )
        
        # Handle 404 specifically
        if e.status_code == 404:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "channel_not_found",
                    "message": f"Notification channel with ID {channel_id} not found"
                }
            )
        
        raise HTTPException(
            status_code=e.status_code or 503,
            detail={
                "error": "core_data_service_error",
                "message": f"Failed to update channel via Core Data Service: {e.message}",
                "details": e.details
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        await logger.aerror("Failed to update notification channel", channel_id=channel_id, error=str(e))
        raise HTTPException(
            status_code=500,
            detail={
                "error": "update_failed",
                "message": "Failed to update notification channel",
                "details": {"channel_id": channel_id, "reason": str(e)}
            }
        )


@router.delete("/{channel_id}")
async def delete_notification_channel(channel_id: str):
    """
    Delete notification channel - REDESIGNED to use Core Data Service API
    """
    try:
        # Get Core Data Service client
        client = await get_core_data_client()
        
        # Delete channel via Core Data Service
        await client.delete_notification_channel(channel_id)
        
        await logger.ainfo(
            "Notification channel deleted via Core Data Service",
            channel_id=channel_id
        )
        
        return {"message": "Notification channel deleted successfully"}
        
    except CoreDataServiceError as e:
        await logger.aerror(
            "Core Data Service error while deleting channel",
            error=str(e),
            status_code=e.status_code,
            channel_id=channel_id
        )
        
        # Handle 404 specifically
        if e.status_code == 404:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "channel_not_found",
                    "message": f"Notification channel with ID {channel_id} not found"
                }
            )
        
        raise HTTPException(
            status_code=e.status_code or 503,
            detail={
                "error": "core_data_service_error",
                "message": f"Failed to delete channel via Core Data Service: {e.message}",
                "details": e.details
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        await logger.aerror("Failed to delete notification channel", channel_id=channel_id, error=str(e))
        raise HTTPException(
            status_code=500,
            detail={
                "error": "deletion_failed",
                "message": "Failed to delete notification channel",
                "details": {"channel_id": channel_id, "reason": str(e)}
            }
        )


@router.post("/{channel_id}/test")
async def test_notification_channel(channel_id: str):
    """
    Test notification channel delivery - REDESIGNED to use Core Data Service API
    """
    try:
        # Get Core Data Service client
        client = await get_core_data_client()
        
        # Test channel via Core Data Service
        result = await client.test_notification_channel(channel_id)
        
        await logger.ainfo(
            "Notification channel test triggered via Core Data Service",
            channel_id=channel_id
        )
        
        return result
        
    except CoreDataServiceError as e:
        await logger.aerror(
            "Core Data Service error while testing channel",
            error=str(e),
            status_code=e.status_code,
            channel_id=channel_id
        )
        
        # Handle 404 specifically
        if e.status_code == 404:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "channel_not_found",
                    "message": f"Notification channel with ID {channel_id} not found"
                }
            )
        
        raise HTTPException(
            status_code=e.status_code or 503,
            detail={
                "error": "core_data_service_error",
                "message": f"Failed to test channel via Core Data Service: {e.message}",
                "details": e.details
            }
        )
    except Exception as e:
        await logger.aerror("Failed to test notification channel", channel_id=channel_id, error=str(e))
        raise HTTPException(
            status_code=500,
            detail={
                "error": "test_failed",
                "message": "Failed to test notification channel",
                "details": {"channel_id": channel_id, "reason": str(e)}
            }
        )