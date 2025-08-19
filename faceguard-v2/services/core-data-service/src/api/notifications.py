"""
FACEGUARD V2 CORE DATA SERVICE - NOTIFICATIONS API
Rule 2: Zero Placeholder Code - Real REST API endpoints
Rule 3: Error-First Development - Proper HTTP status codes
Critical: NO 501 "Not Implemented" errors anywhere
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import structlog

from storage.database import get_db_session
from services.notification_service import NotificationService
from domain.schemas import (
    NotificationChannelCreate, NotificationChannelUpdate, NotificationChannelResponse,
    AlertRuleCreate, AlertRuleUpdate, AlertRuleResponse, AlertRuleListResponse,
    NotificationLogCreate, NotificationLogResponse, NotificationLogListResponse,
    NotificationAnalytics, SuccessResponse, ErrorResponse
)

logger = structlog.get_logger(__name__)
router = APIRouter(prefix="/notifications", tags=["notifications"])


# =====================================
# NOTIFICATION CHANNELS ENDPOINTS
# =====================================

@router.post("/channels", response_model=NotificationChannelResponse, status_code=201)
async def create_notification_channel(
    channel_data: NotificationChannelCreate,
    session: AsyncSession = Depends(get_db_session)
) -> NotificationChannelResponse:
    """
    Create new notification channel
    Rule 2: Zero Placeholder Code - Real channel creation
    Rule 3: Error-First Development - Comprehensive validation
    
    Returns:
        NotificationChannelResponse: Created channel data
        
    HTTP Status Codes:
        201: Channel created successfully
        400: Validation error or duplicate channel name
        500: Internal server error
    """
    try:
        await logger.ainfo("Creating new notification channel", 
                           channel_name=channel_data.channel_name,
                           channel_type=channel_data.channel_type)
        
        notification_service = NotificationService(session)
        channel = await notification_service.create_notification_channel(channel_data)
        
        await logger.ainfo("Notification channel created successfully", 
                           channel_id=channel.id,
                           channel_name=channel.channel_name)
        return channel
        
    except ValueError as e:
        await logger.awarn("Channel creation validation failed", error=str(e))
        raise HTTPException(status_code=400, detail={
            "error": "validation_error",
            "message": str(e)
        })
    except Exception as e:
        await logger.aerror("Channel creation failed", error=str(e))
        raise HTTPException(status_code=500, detail={
            "error": "internal_error", 
            "message": "Failed to create notification channel"
        })


@router.get("/channels/{channel_id}", response_model=NotificationChannelResponse)
async def get_notification_channel(
    channel_id: str,
    session: AsyncSession = Depends(get_db_session)
) -> NotificationChannelResponse:
    """
    Get notification channel by ID
    Rule 3: Error-First Development - Proper 404 handling
    
    Args:
        channel_id: UUID string
        
    Returns:
        NotificationChannelResponse: Channel data
        
    HTTP Status Codes:
        200: Channel found
        404: Channel not found
        500: Internal server error
    """
    try:
        await logger.ainfo("Retrieving notification channel", channel_id=channel_id)
        
        notification_service = NotificationService(session)
        channel = await notification_service.get_notification_channel(channel_id)
        
        if not channel:
            await logger.ainfo("Notification channel not found", channel_id=channel_id)
            raise HTTPException(status_code=404, detail={
                "error": "not_found",
                "message": f"Notification channel with ID '{channel_id}' not found"
            })
        
        await logger.ainfo("Notification channel retrieved successfully", 
                           channel_id=channel.id,
                           channel_name=channel.channel_name)
        return channel
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        await logger.aerror("Channel retrieval failed", channel_id=channel_id, error=str(e))
        raise HTTPException(status_code=500, detail={
            "error": "internal_error",
            "message": "Failed to retrieve notification channel"
        })


@router.get("/channels", response_model=list)
async def list_notification_channels(
    active_only: bool = Query(default=False, description="Filter to active channels only"),
    session: AsyncSession = Depends(get_db_session)
) -> list:
    """
    List notification channels
    Rule 2: Zero Placeholder Code - Real channel listing
    
    Query Parameters:
        active_only: Filter to active channels only (default: false)
        
    Returns:
        List[NotificationChannelResponse]: List of channels
        
    HTTP Status Codes:
        200: Channels retrieved successfully
        500: Internal server error
    """
    try:
        await logger.ainfo("Listing notification channels", active_only=active_only)
        
        notification_service = NotificationService(session)
        channels = await notification_service.list_notification_channels(active_only=active_only)
        
        await logger.ainfo("Notification channels listed successfully", 
                           channel_count=len(channels),
                           active_only=active_only)
        return channels
        
    except Exception as e:
        await logger.aerror("Channel listing failed", error=str(e))
        raise HTTPException(status_code=500, detail={
            "error": "internal_error",
            "message": "Failed to list notification channels"
        })


@router.put("/channels/{channel_id}", response_model=NotificationChannelResponse)
async def update_notification_channel(
    channel_id: str,
    channel_data: NotificationChannelUpdate,
    session: AsyncSession = Depends(get_db_session)
) -> NotificationChannelResponse:
    """
    Update notification channel
    Rule 2: Zero Placeholder Code - Real channel update
    Rule 3: Error-First Development - Proper validation and 404 handling
    
    Args:
        channel_id: UUID string
        channel_data: Partial update data
        
    Returns:
        NotificationChannelResponse: Updated channel data
        
    HTTP Status Codes:
        200: Channel updated successfully
        400: Validation error
        404: Channel not found
        500: Internal server error
    """
    try:
        await logger.ainfo("Updating notification channel", channel_id=channel_id)
        
        notification_service = NotificationService(session)
        channel = await notification_service.update_notification_channel(channel_id, channel_data)
        
        if not channel:
            await logger.ainfo("Notification channel not found for update", channel_id=channel_id)
            raise HTTPException(status_code=404, detail={
                "error": "not_found",
                "message": f"Notification channel with ID '{channel_id}' not found"
            })
        
        await logger.ainfo("Notification channel updated successfully", 
                           channel_id=channel.id,
                           channel_name=channel.channel_name)
        return channel
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except ValueError as e:
        await logger.awarn("Channel update validation failed", channel_id=channel_id, error=str(e))
        raise HTTPException(status_code=400, detail={
            "error": "validation_error",
            "message": str(e)
        })
    except Exception as e:
        await logger.aerror("Channel update failed", channel_id=channel_id, error=str(e))
        raise HTTPException(status_code=500, detail={
            "error": "internal_error",
            "message": "Failed to update notification channel"
        })


@router.delete("/channels/{channel_id}", status_code=204)
async def delete_notification_channel(
    channel_id: str,
    session: AsyncSession = Depends(get_db_session)
) -> None:
    """
    Delete notification channel
    Rule 3: Error-First Development - Proper 404 handling
    
    Args:
        channel_id: UUID string
        
    HTTP Status Codes:
        204: Channel deleted successfully
        404: Channel not found
        500: Internal server error
    """
    try:
        await logger.ainfo("Deleting notification channel", channel_id=channel_id)
        
        notification_service = NotificationService(session)
        deleted = await notification_service.delete_notification_channel(channel_id)
        
        if not deleted:
            await logger.ainfo("Notification channel not found for deletion", channel_id=channel_id)
            raise HTTPException(status_code=404, detail={
                "error": "not_found",
                "message": f"Notification channel with ID '{channel_id}' not found"
            })
        
        await logger.ainfo("Notification channel deleted successfully", channel_id=channel_id)
        # Return 204 No Content (no response body)
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        await logger.aerror("Channel deletion failed", channel_id=channel_id, error=str(e))
        raise HTTPException(status_code=500, detail={
            "error": "internal_error",
            "message": "Failed to delete notification channel"
        })


# =====================================
# ALERT RULES ENDPOINTS
# =====================================

@router.post("/alert-rules", response_model=AlertRuleResponse, status_code=201)
async def create_alert_rule(
    rule_data: AlertRuleCreate,
    session: AsyncSession = Depends(get_db_session)
) -> AlertRuleResponse:
    """
    Create new alert rule
    Rule 2: Zero Placeholder Code - Real alert rule creation
    Rule 3: Error-First Development - Comprehensive validation
    
    Returns:
        AlertRuleResponse: Created rule data
        
    HTTP Status Codes:
        201: Rule created successfully
        400: Validation error
        500: Internal server error
    """
    try:
        await logger.ainfo("Creating new alert rule", 
                           rule_name=rule_data.rule_name,
                           priority=rule_data.priority)
        
        notification_service = NotificationService(session)
        rule = await notification_service.create_alert_rule(rule_data)
        
        await logger.ainfo("Alert rule created successfully", 
                           rule_id=rule.id,
                           rule_name=rule.rule_name)
        return rule
        
    except ValueError as e:
        await logger.awarn("Alert rule creation validation failed", error=str(e))
        raise HTTPException(status_code=400, detail={
            "error": "validation_error",
            "message": str(e)
        })
    except Exception as e:
        await logger.aerror("Alert rule creation failed", error=str(e))
        raise HTTPException(status_code=500, detail={
            "error": "internal_error", 
            "message": "Failed to create alert rule"
        })


@router.get("/alert-rules/{rule_id}", response_model=AlertRuleResponse)
async def get_alert_rule(
    rule_id: str,
    session: AsyncSession = Depends(get_db_session)
) -> AlertRuleResponse:
    """
    Get alert rule by ID
    Rule 3: Error-First Development - Proper 404 handling
    
    Args:
        rule_id: UUID string
        
    Returns:
        AlertRuleResponse: Rule data
        
    HTTP Status Codes:
        200: Rule found
        404: Rule not found
        500: Internal server error
    """
    try:
        await logger.ainfo("Retrieving alert rule", rule_id=rule_id)
        
        notification_service = NotificationService(session)
        rule = await notification_service.get_alert_rule(rule_id)
        
        if not rule:
            await logger.ainfo("Alert rule not found", rule_id=rule_id)
            raise HTTPException(status_code=404, detail={
                "error": "not_found",
                "message": f"Alert rule with ID '{rule_id}' not found"
            })
        
        await logger.ainfo("Alert rule retrieved successfully", 
                           rule_id=rule.id,
                           rule_name=rule.rule_name)
        return rule
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        await logger.aerror("Alert rule retrieval failed", rule_id=rule_id, error=str(e))
        raise HTTPException(status_code=500, detail={
            "error": "internal_error",
            "message": "Failed to retrieve alert rule"
        })


@router.get("/alert-rules", response_model=AlertRuleListResponse)
async def list_alert_rules(
    page: int = Query(default=1, ge=1, description="Page number starting from 1"),
    limit: int = Query(default=50, ge=1, le=100, description="Number of rules per page"),
    active_only: bool = Query(default=False, description="Filter to active rules only"),
    session: AsyncSession = Depends(get_db_session)
) -> AlertRuleListResponse:
    """
    List alert rules with pagination
    Rule 2: Zero Placeholder Code - Real pagination implementation
    
    Query Parameters:
        page: Page number (default: 1)
        limit: Items per page (default: 50, max: 100)
        active_only: Filter to active rules only (default: false)
        
    Returns:
        AlertRuleListResponse: Paginated rule list
        
    HTTP Status Codes:
        200: Rules retrieved successfully
        400: Invalid pagination parameters
        500: Internal server error
    """
    try:
        await logger.ainfo("Listing alert rules", 
                           page=page, 
                           limit=limit, 
                           active_only=active_only)
        
        notification_service = NotificationService(session)
        rules = await notification_service.list_alert_rules(
            page=page,
            limit=limit,
            active_only=active_only
        )
        
        await logger.ainfo("Alert rules listed successfully", 
                           total=rules.total, 
                           returned=len(rules.alert_rules))
        return rules
        
    except ValueError as e:
        await logger.awarn("Alert rule listing validation failed", error=str(e))
        raise HTTPException(status_code=400, detail={
            "error": "validation_error",
            "message": str(e)
        })
    except Exception as e:
        await logger.aerror("Alert rule listing failed", error=str(e))
        raise HTTPException(status_code=500, detail={
            "error": "internal_error",
            "message": "Failed to list alert rules"
        })


@router.put("/alert-rules/{rule_id}", response_model=AlertRuleResponse)
async def update_alert_rule(
    rule_id: str,
    rule_data: AlertRuleUpdate,
    session: AsyncSession = Depends(get_db_session)
) -> AlertRuleResponse:
    """
    Update alert rule
    Rule 2: Zero Placeholder Code - Real rule update
    Rule 3: Error-First Development - Proper validation and 404 handling
    
    Args:
        rule_id: UUID string
        rule_data: Partial update data
        
    Returns:
        AlertRuleResponse: Updated rule data
        
    HTTP Status Codes:
        200: Rule updated successfully
        400: Validation error
        404: Rule not found
        500: Internal server error
    """
    try:
        await logger.ainfo("Updating alert rule", rule_id=rule_id)
        
        notification_service = NotificationService(session)
        rule = await notification_service.update_alert_rule(rule_id, rule_data)
        
        if not rule:
            await logger.ainfo("Alert rule not found for update", rule_id=rule_id)
            raise HTTPException(status_code=404, detail={
                "error": "not_found",
                "message": f"Alert rule with ID '{rule_id}' not found"
            })
        
        await logger.ainfo("Alert rule updated successfully", 
                           rule_id=rule.id,
                           rule_name=rule.rule_name)
        return rule
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except ValueError as e:
        await logger.awarn("Alert rule update validation failed", rule_id=rule_id, error=str(e))
        raise HTTPException(status_code=400, detail={
            "error": "validation_error",
            "message": str(e)
        })
    except Exception as e:
        await logger.aerror("Alert rule update failed", rule_id=rule_id, error=str(e))
        raise HTTPException(status_code=500, detail={
            "error": "internal_error",
            "message": "Failed to update alert rule"
        })


@router.delete("/alert-rules/{rule_id}", status_code=204)
async def delete_alert_rule(
    rule_id: str,
    session: AsyncSession = Depends(get_db_session)
) -> None:
    """
    Delete alert rule
    Rule 3: Error-First Development - Proper 404 handling
    
    Args:
        rule_id: UUID string
        
    HTTP Status Codes:
        204: Rule deleted successfully
        404: Rule not found
        500: Internal server error
    """
    try:
        await logger.ainfo("Deleting alert rule", rule_id=rule_id)
        
        notification_service = NotificationService(session)
        deleted = await notification_service.delete_alert_rule(rule_id)
        
        if not deleted:
            await logger.ainfo("Alert rule not found for deletion", rule_id=rule_id)
            raise HTTPException(status_code=404, detail={
                "error": "not_found",
                "message": f"Alert rule with ID '{rule_id}' not found"
            })
        
        await logger.ainfo("Alert rule deleted successfully", rule_id=rule_id)
        # Return 204 No Content (no response body)
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        await logger.aerror("Alert rule deletion failed", rule_id=rule_id, error=str(e))
        raise HTTPException(status_code=500, detail={
            "error": "internal_error",
            "message": "Failed to delete alert rule"
        })


# =====================================
# NOTIFICATION LOGS ENDPOINTS
# =====================================

@router.post("/logs", response_model=NotificationLogResponse, status_code=201)
async def create_notification_log(
    log_data: NotificationLogCreate,
    session: AsyncSession = Depends(get_db_session)
) -> NotificationLogResponse:
    """
    Create new notification log entry
    Rule 2: Zero Placeholder Code - Real log creation
    Rule 3: Error-First Development - Comprehensive validation
    
    Returns:
        NotificationLogResponse: Created log data
        
    HTTP Status Codes:
        201: Log created successfully
        400: Validation error
        500: Internal server error
    """
    try:
        await logger.ainfo("Creating new notification log", 
                           recipient=log_data.recipient,
                           channel_id=log_data.channel_id)
        
        notification_service = NotificationService(session)
        log = await notification_service.create_notification_log(log_data)
        
        await logger.ainfo("Notification log created successfully", 
                           log_id=log.id,
                           recipient=log.recipient)
        return log
        
    except ValueError as e:
        await logger.awarn("Notification log creation validation failed", error=str(e))
        raise HTTPException(status_code=400, detail={
            "error": "validation_error",
            "message": str(e)
        })
    except Exception as e:
        await logger.aerror("Notification log creation failed", error=str(e))
        raise HTTPException(status_code=500, detail={
            "error": "internal_error", 
            "message": "Failed to create notification log"
        })


@router.get("/logs", response_model=NotificationLogListResponse)
async def list_notification_logs(
    page: int = Query(default=1, ge=1, description="Page number starting from 1"),
    limit: int = Query(default=50, ge=1, le=100, description="Number of logs per page"),
    delivery_id: Optional[str] = Query(default=None, description="Filter by delivery ID"),
    status: Optional[str] = Query(default=None, description="Filter by delivery status"),
    recipient: Optional[str] = Query(default=None, description="Filter by recipient"),
    session: AsyncSession = Depends(get_db_session)
) -> NotificationLogListResponse:
    """
    List notification logs with pagination and filtering
    Rule 2: Zero Placeholder Code - Real pagination implementation
    
    Query Parameters:
        page: Page number (default: 1)
        limit: Items per page (default: 50, max: 100)
        delivery_id: Filter by delivery ID (optional)
        status: Filter by delivery status (optional)
        recipient: Filter by recipient (optional)
        
    Returns:
        NotificationLogListResponse: Paginated log list
        
    HTTP Status Codes:
        200: Logs retrieved successfully
        400: Invalid parameters
        500: Internal server error
    """
    try:
        await logger.ainfo("Listing notification logs", 
                           page=page, 
                           limit=limit,
                           delivery_id=delivery_id,
                           status=status,
                           recipient=recipient)
        
        notification_service = NotificationService(session)
        logs = await notification_service.list_notification_logs(
            page=page,
            limit=limit,
            delivery_id=delivery_id,
            status=status,
            recipient=recipient
        )
        
        await logger.ainfo("Notification logs listed successfully", 
                           total=logs.total, 
                           returned=len(logs.logs))
        return logs
        
    except ValueError as e:
        await logger.awarn("Notification log listing validation failed", error=str(e))
        raise HTTPException(status_code=400, detail={
            "error": "validation_error",
            "message": str(e)
        })
    except Exception as e:
        await logger.aerror("Notification log listing failed", error=str(e))
        raise HTTPException(status_code=500, detail={
            "error": "internal_error",
            "message": "Failed to list notification logs"
        })


# =====================================
# ANALYTICS ENDPOINT
# =====================================

@router.get("/analytics", response_model=NotificationAnalytics)
async def get_notification_analytics(
    days: int = Query(default=7, ge=1, le=365, description="Number of days for analytics"),
    session: AsyncSession = Depends(get_db_session)
) -> NotificationAnalytics:
    """
    Get notification system analytics
    Rule 2: Zero Placeholder Code - Real analytics implementation
    
    Query Parameters:
        days: Number of days for analytics period (default: 7, max: 365)
        
    Returns:
        NotificationAnalytics: System analytics data
        
    HTTP Status Codes:
        200: Analytics retrieved successfully
        400: Invalid parameters
        500: Internal server error
    """
    try:
        await logger.ainfo("Getting notification analytics", days=days)
        
        notification_service = NotificationService(session)
        analytics = await notification_service.get_notification_analytics(days=days)
        
        await logger.ainfo("Notification analytics retrieved successfully", 
                           total_notifications=analytics.total_notifications,
                           success_rate=analytics.success_rate)
        return analytics
        
    except ValueError as e:
        await logger.awarn("Notification analytics validation failed", error=str(e))
        raise HTTPException(status_code=400, detail={
            "error": "validation_error",
            "message": str(e)
        })
    except Exception as e:
        await logger.aerror("Notification analytics failed", error=str(e))
        raise HTTPException(status_code=500, detail={
            "error": "internal_error",
            "message": "Failed to retrieve notification analytics"
        })