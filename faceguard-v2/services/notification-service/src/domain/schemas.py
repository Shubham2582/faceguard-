"""
FACEGUARD V2 NOTIFICATION SERVICE - PYDANTIC SCHEMAS  
Rule 2: Zero Placeholder Code - Real request/response validation
Rule 3: Error-First Development - Comprehensive field validation

Notification-specific schemas for multi-channel delivery
"""

from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal
from enum import Enum


# =============================================================================
# NOTIFICATION DELIVERY SCHEMAS
# =============================================================================

class DeliveryChannelType(str, Enum):
    """Supported notification delivery channels"""
    EMAIL = "email"
    SMS = "sms" 
    WEBHOOK = "webhook"
    WEBSOCKET = "websocket"
    SLACK = "slack"
    TEAMS = "teams"


class DeliveryStatus(str, Enum):
    """Notification delivery status"""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    BOUNCED = "bounced"
    RETRY = "retry"


class AlertPriority(str, Enum):
    """Alert priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertStatus(str, Enum):
    """Alert instance status"""
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    ESCALATED = "escalated"


# =============================================================================
# NOTIFICATION CHANNEL SCHEMAS
# =============================================================================

class NotificationChannelBase(BaseModel):
    """Base notification channel schema"""
    channel_name: str = Field(..., min_length=1, max_length=100, description="Unique channel name")
    channel_type: DeliveryChannelType = Field(..., description="Channel type")
    configuration: Dict[str, Any] = Field(..., description="Channel-specific configuration")
    is_active: bool = Field(default=True, description="Channel active status")
    rate_limit_per_minute: int = Field(default=60, ge=1, le=1000, description="Rate limit per minute")
    retry_attempts: int = Field(default=3, ge=0, le=10, description="Max retry attempts")
    timeout_seconds: int = Field(default=30, ge=5, le=300, description="Request timeout")
    
    @validator('configuration')
    def validate_configuration(cls, v, values):
        """Validate configuration based on channel type"""
        channel_type = values.get('channel_type')
        
        if channel_type == DeliveryChannelType.EMAIL:
            required_fields = ['email_address']
            for field in required_fields:
                if field not in v:
                    raise ValueError(f"Email channel requires {field} in configuration")
            
            # Validate email format
            email = v.get('email_address')
            if email and '@' not in email:
                raise ValueError("Invalid email address format")
                
        elif channel_type == DeliveryChannelType.SMS:
            required_fields = ['phone_number']
            for field in required_fields:
                if field not in v:
                    raise ValueError(f"SMS channel requires {field} in configuration")
                    
        elif channel_type == DeliveryChannelType.WEBHOOK:
            required_fields = ['url']
            for field in required_fields:
                if field not in v:
                    raise ValueError(f"Webhook channel requires {field} in configuration")
                    
        return v


class NotificationChannelCreate(NotificationChannelBase):
    """Schema for creating notification channels"""
    pass


class NotificationChannelUpdate(BaseModel):
    """Schema for updating notification channels (all fields optional)"""
    channel_name: Optional[str] = Field(None, min_length=1, max_length=100)
    configuration: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None
    rate_limit_per_minute: Optional[int] = Field(None, ge=1, le=1000)
    retry_attempts: Optional[int] = Field(None, ge=0, le=10)
    timeout_seconds: Optional[int] = Field(None, ge=5, le=300)


class NotificationChannelResponse(NotificationChannelBase):
    """Schema for notification channel responses"""
    id: str
    created_at: datetime
    updated_at: datetime
    last_used_at: Optional[datetime] = Field(None, description="Last time channel was used")
    delivery_count: int = Field(default=0, description="Total deliveries via this channel")
    success_rate: float = Field(default=0.0, description="Delivery success rate")
    
    @validator('id', pre=True)
    def convert_uuid_to_string(cls, v):
        """Convert UUID objects to strings"""
        if hasattr(v, '__str__'):
            return str(v)
        return v
    
    class Config:
        from_attributes = True


# =============================================================================
# ALERT RULE SCHEMAS  
# =============================================================================

class AlertRuleBase(BaseModel):
    """Base alert rule schema"""
    rule_name: str = Field(..., min_length=1, max_length=200, description="Alert rule name")
    description: Optional[str] = Field(None, description="Rule description")
    is_active: bool = Field(default=True, description="Rule active status")
    priority: AlertPriority = Field(default=AlertPriority.MEDIUM, description="Alert priority")
    trigger_conditions: Dict[str, Any] = Field(..., description="Trigger conditions in JSON format")
    cooldown_minutes: int = Field(default=30, ge=0, le=1440, description="Cooldown between alerts")
    escalation_minutes: Optional[int] = Field(None, ge=0, le=1440, description="Escalation time")
    auto_resolve_minutes: Optional[int] = Field(None, ge=0, le=10080, description="Auto-resolve time")
    notification_channels: List[str] = Field(..., min_items=1, description="Notification channel IDs")
    notification_template: Optional[Dict[str, Any]] = Field(None, description="Custom message template")
    
    @validator('trigger_conditions')
    def validate_trigger_conditions(cls, v):
        """Basic validation for trigger conditions"""
        if not isinstance(v, dict):
            raise ValueError("Trigger conditions must be a dictionary")
        
        valid_keys = [
            "person_ids", "camera_ids", "confidence_min", "confidence_max",
            "time_ranges", "any_person", "excluded_persons", "location_ids"
        ]
        
        if not any(key in v for key in valid_keys):
            raise ValueError(f"Trigger conditions must contain at least one of: {valid_keys}")
            
        return v


class AlertRuleCreate(AlertRuleBase):
    """Schema for creating alert rules"""
    created_by: Optional[str] = Field(None, max_length=100, description="Created by user")


class AlertRuleUpdate(BaseModel):
    """Schema for updating alert rules (all fields optional)"""
    rule_name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    is_active: Optional[bool] = None
    priority: Optional[AlertPriority] = None
    trigger_conditions: Optional[Dict[str, Any]] = None
    cooldown_minutes: Optional[int] = Field(None, ge=0, le=1440)
    escalation_minutes: Optional[int] = Field(None, ge=0, le=1440)
    auto_resolve_minutes: Optional[int] = Field(None, ge=0, le=10080)
    notification_channels: Optional[List[str]] = None
    notification_template: Optional[Dict[str, Any]] = None


class AlertRuleResponse(AlertRuleBase):
    """Schema for alert rule responses"""
    id: str
    created_by: Optional[str]
    created_at: datetime
    updated_at: datetime
    trigger_count: int = Field(default=0, description="Number of times rule has triggered")
    last_triggered_at: Optional[datetime] = Field(None, description="Last time rule triggered")
    
    @validator('id', pre=True)
    def convert_uuid_to_string(cls, v):
        """Convert UUID objects to strings"""
        if hasattr(v, '__str__'):
            return str(v)
        return v
    
    class Config:
        from_attributes = True


# =============================================================================
# ALERT INSTANCE SCHEMAS
# =============================================================================

class AlertInstanceBase(BaseModel):
    """Base alert instance schema"""
    rule_id: str = Field(..., description="Alert rule UUID")
    person_id: Optional[str] = Field(None, description="Person UUID")
    camera_id: Optional[str] = Field(None, description="Camera UUID")
    sighting_id: Optional[str] = Field(None, description="Sighting UUID")
    confidence_score: Optional[Decimal] = Field(None, ge=0.0, le=1.0, description="Detection confidence")
    alert_priority: AlertPriority = Field(..., description="Alert priority")
    alert_message: Optional[str] = Field(None, description="Alert message")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional alert metadata")


class AlertInstanceCreate(AlertInstanceBase):
    """Schema for creating alert instances"""
    pass


class AlertInstanceResponse(AlertInstanceBase):
    """Schema for alert instance responses"""
    id: str
    triggered_at: datetime
    status: AlertStatus
    acknowledged_at: Optional[datetime]
    acknowledged_by: Optional[str]
    resolved_at: Optional[datetime]
    escalated_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    # Related data for convenience
    rule_name: Optional[str] = Field(None, description="Rule name for convenience")
    person_name: Optional[str] = Field(None, description="Person name for convenience")
    camera_name: Optional[str] = Field(None, description="Camera name for convenience")
    
    # Delivery tracking
    notification_count: int = Field(default=0, description="Number of notifications sent")
    delivery_success_rate: float = Field(default=0.0, description="Delivery success rate")
    
    @validator('id', pre=True)
    def convert_uuid_to_string(cls, v):
        """Convert UUID objects to strings"""
        if hasattr(v, '__str__'):
            return str(v)
        return v
    
    class Config:
        from_attributes = True


# =============================================================================
# NOTIFICATION DELIVERY SCHEMAS
# =============================================================================

class NotificationDeliveryRequest(BaseModel):
    """Schema for triggering notification delivery"""
    alert_id: str = Field(..., description="Alert instance ID")
    channel_ids: Optional[List[str]] = Field(None, description="Specific channels to deliver to")
    override_cooldown: bool = Field(default=False, description="Override cooldown period")
    test_mode: bool = Field(default=False, description="Test delivery without saving")


class NotificationDeliveryResponse(BaseModel):
    """Schema for delivery operation results"""
    alert_id: str
    total_channels: int
    successful_deliveries: int
    failed_deliveries: int
    delivery_rate: float = Field(..., ge=0.0, le=100.0, description="Success rate percentage")
    delivery_details: List[Dict[str, Any]] = Field(default_factory=list)
    delivered_at: datetime
    
    
class NotificationLogResponse(BaseModel):
    """Schema for notification log responses"""
    id: str
    alert_id: str
    channel_id: str
    delivery_status: DeliveryStatus
    sent_at: Optional[datetime]
    delivered_at: Optional[datetime]
    error_message: Optional[str]
    error_code: Optional[str]
    retry_count: int
    external_id: Optional[str]
    delivery_metadata: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    
    # Related data
    channel_name: Optional[str] = Field(None, description="Channel name for convenience")
    channel_type: Optional[DeliveryChannelType] = Field(None, description="Channel type for convenience")
    
    @validator('id', pre=True)
    def convert_uuid_to_string(cls, v):
        if hasattr(v, '__str__'):
            return str(v)
        return v
    
    class Config:
        from_attributes = True


# =============================================================================
# BULK OPERATION SCHEMAS
# =============================================================================

class BulkNotificationRequest(BaseModel):
    """Schema for bulk notification delivery"""
    alert_ids: List[str] = Field(..., min_items=1, max_items=100, description="Alert IDs to process")
    channel_filter: Optional[List[DeliveryChannelType]] = Field(None, description="Filter by channel types")
    priority_filter: Optional[List[AlertPriority]] = Field(None, description="Filter by priority")


class BulkNotificationResponse(BaseModel):
    """Schema for bulk operation results"""
    total_alerts: int
    processed_alerts: int
    successful_notifications: int
    failed_notifications: int
    processing_time_seconds: float
    results: List[NotificationDeliveryResponse]


# =============================================================================
# ANALYTICS AND MONITORING SCHEMAS
# =============================================================================

class NotificationAnalytics(BaseModel):
    """Schema for notification system analytics"""
    total_alerts: int
    total_notifications: int
    delivery_success_rate: float
    channel_performance: Dict[str, Dict[str, Any]]
    alert_frequency: Dict[str, int]
    top_triggered_rules: List[Dict[str, Any]]
    delivery_volume_by_hour: List[Dict[str, Any]]
    error_summary: Dict[str, int]
    period_start: datetime
    period_end: datetime
    generated_at: datetime


class ChannelTestRequest(BaseModel):
    """Schema for testing notification channels"""
    channel_id: str
    test_message: str = Field(default="Test notification from FaceGuard V2", max_length=500)
    test_recipient: Optional[str] = Field(None, description="Override recipient for testing")


class ChannelTestResponse(BaseModel):
    """Schema for channel test results"""
    success: bool
    message: str
    channel_name: str
    channel_type: DeliveryChannelType
    test_details: Dict[str, Any]
    tested_at: datetime


# =============================================================================
# COMMON RESPONSE SCHEMAS
# =============================================================================

class ErrorResponse(BaseModel):
    """Standard error response schema"""
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")


class SuccessResponse(BaseModel):
    """Standard success response schema"""
    success: bool = Field(default=True, description="Operation success flag")
    message: str = Field(..., description="Success message")
    data: Optional[Dict[str, Any]] = Field(None, description="Response data")


class PaginatedResponse(BaseModel):
    """Base schema for paginated responses"""
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    limit: int = Field(..., description="Items per page")
    
    @validator('page')
    def validate_page(cls, v):
        if v < 1:
            raise ValueError("Page must be >= 1")
        return v
    
    @validator('limit')
    def validate_limit(cls, v):
        if not (1 <= v <= 200):
            raise ValueError("Limit must be between 1 and 200")
        return v


class AlertRuleListResponse(PaginatedResponse):
    """Schema for paginated alert rule lists"""
    alert_rules: List[AlertRuleResponse] = Field(..., description="List of alert rules")


class AlertInstanceListResponse(PaginatedResponse):
    """Schema for paginated alert instance lists"""
    alert_instances: List[AlertInstanceResponse] = Field(..., description="List of alert instances")


class NotificationLogListResponse(PaginatedResponse):
    """Schema for paginated notification log lists"""
    notification_logs: List[NotificationLogResponse] = Field(..., description="List of notification logs")


# =============================================================================
# WEBHOOK SCHEMAS
# =============================================================================

class WebhookPayload(BaseModel):
    """Standard webhook payload format"""
    event_type: str = Field(..., description="Type of event")
    alert_id: str = Field(..., description="Alert instance ID")
    timestamp: datetime = Field(..., description="Event timestamp")
    alert_data: Dict[str, Any] = Field(..., description="Alert details")
    source: str = Field(default="faceguard_v2", description="Source system")
    signature: Optional[str] = Field(None, description="Payload signature for verification")


class WebhookDeliveryStatus(BaseModel):
    """Webhook delivery status update"""
    webhook_id: str
    delivery_status: DeliveryStatus
    response_code: Optional[int] = None
    response_message: Optional[str] = None
    delivery_time_ms: Optional[int] = None
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# =============================================================================
# ADDITIONAL NOTIFICATION SERVICE SCHEMAS
# =============================================================================

class NotificationChannelCreateRequest(NotificationChannelBase):
    """Schema for creating notification channels"""
    pass


class NotificationChannelUpdateRequest(BaseModel):
    """Schema for updating notification channels (all fields optional)"""
    channel_name: Optional[str] = Field(None, min_length=1, max_length=100)
    channel_type: Optional[DeliveryChannelType] = None
    configuration: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None
    rate_limit_per_minute: Optional[int] = Field(None, ge=1, le=1000)
    retry_attempts: Optional[int] = Field(None, ge=0, le=10)
    timeout_seconds: Optional[int] = Field(None, ge=5, le=300)


class NotificationChannelListResponse(PaginatedResponse):
    """Schema for paginated notification channel lists"""
    channels: List[NotificationChannelResponse] = Field(..., description="List of notification channels")


class NotificationChannelTestRequest(BaseModel):
    """Schema for testing notification channels"""
    test_subject: Optional[str] = Field(None, max_length=200, description="Test message subject")
    test_message: str = Field(default="Test notification from FaceGuard V2", max_length=1000, description="Test message content")
    test_recipient: Optional[str] = Field(None, description="Override recipient for testing (email/phone/URL)")


class AlertRuleCreateRequest(AlertRuleBase):
    """Schema for creating alert rules"""
    created_by: Optional[str] = Field(None, max_length=100, description="Created by user")


class AlertRuleUpdateRequest(BaseModel):
    """Schema for updating alert rules (all fields optional)"""
    rule_name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    is_active: Optional[bool] = None
    priority: Optional[AlertPriority] = None
    trigger_conditions: Optional[Dict[str, Any]] = None
    cooldown_minutes: Optional[int] = Field(None, ge=0, le=1440)
    escalation_minutes: Optional[int] = Field(None, ge=0, le=1440)
    auto_resolve_minutes: Optional[int] = Field(None, ge=0, le=10080)
    notification_channels: Optional[List[str]] = None
    notification_template: Optional[Dict[str, Any]] = None


class AlertInstanceListResponse(PaginatedResponse):
    """Schema for paginated alert instance lists"""
    instances: List[AlertInstanceResponse] = Field(..., description="List of alert instances")


class NotificationDeliveryRequest(BaseModel):
    """Schema for single notification delivery request"""
    subject: str = Field(..., min_length=1, max_length=200, description="Notification subject")
    message: str = Field(..., min_length=1, max_length=5000, description="Notification message content")
    recipient: Optional[str] = Field(None, description="Optional recipient override")
    channel_ids: Optional[List[str]] = Field(None, description="Specific channel IDs to use")
    priority: AlertPriority = Field(default=AlertPriority.MEDIUM, description="Notification priority")
    template_data: Optional[Dict[str, Any]] = Field(None, description="Template variables")
    delivery_options: Optional[Dict[str, Any]] = Field(None, description="Delivery-specific options")
    ignore_inactive_channels: bool = Field(default=False, description="Ignore inactive channels")


class BulkNotificationRequest(BaseModel):
    """Schema for bulk notification delivery"""
    subject: str = Field(..., min_length=1, max_length=200, description="Notification subject")
    message: str = Field(..., min_length=1, max_length=5000, description="Notification message content")
    recipients: List[str] = Field(..., min_items=1, max_items=1000, description="List of recipients")
    channel_ids: Optional[List[str]] = Field(None, description="Specific channel IDs to use")
    priority: AlertPriority = Field(default=AlertPriority.MEDIUM, description="Notification priority")
    template_data: Optional[Dict[str, Dict[str, Any]]] = Field(None, description="Per-recipient template variables")
    delivery_options: Optional[Dict[str, Any]] = Field(None, description="Delivery-specific options")
    batch_size: Optional[int] = Field(50, ge=1, le=100, description="Batch processing size")


class BulkNotificationResponse(BaseModel):
    """Schema for bulk notification delivery response"""
    bulk_id: str = Field(..., description="Bulk delivery ID")
    status: str = Field(..., description="Overall bulk status")
    message: str = Field(..., description="Status message")
    total_recipients: int = Field(..., description="Total number of recipients")
    delivered_count: Optional[int] = Field(0, description="Successfully delivered count")
    failed_count: Optional[int] = Field(0, description="Failed delivery count")
    processing_count: Optional[int] = Field(0, description="Currently processing count")
    queued_count: Optional[int] = Field(0, description="Queued for processing count")
    delivery_ids: List[str] = Field(default_factory=list, description="Individual delivery IDs")
    estimated_completion_time: Optional[datetime] = Field(None, description="Estimated completion time")
    started_at: Optional[datetime] = Field(None, description="Bulk processing start time")
    completed_at: Optional[datetime] = Field(None, description="Bulk processing completion time")
    tracking_url: Optional[str] = Field(None, description="URL to track bulk delivery status")


class NotificationLogResponse(BaseModel):
    """Schema for notification log entries"""
    id: str
    delivery_id: str
    bulk_delivery_id: Optional[str] = None
    channel_id: Optional[str] = None
    channel_name: Optional[str] = None
    channel_type: Optional[str] = None
    status: str
    message_subject: Optional[str] = None
    recipient: Optional[str] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    created_at: datetime
    delivered_at: Optional[datetime] = None

    @validator('id', pre=True)
    def convert_uuid_to_string(cls, v):
        if hasattr(v, '__str__'):
            return str(v)
        return v

    class Config:
        from_attributes = True


class NotificationLogListResponse(PaginatedResponse):
    """Schema for paginated notification log lists"""
    logs: List[NotificationLogResponse] = Field(..., description="List of notification logs")


class DeliveryAnalyticsResponse(BaseModel):
    """Schema for delivery analytics and metrics"""
    period_start: datetime
    period_end: datetime
    total_notifications: int
    delivered_count: int
    failed_count: int
    processing_count: int
    success_rate: float
    unique_deliveries: int
    unique_recipients: int
    average_delivery_time_seconds: float
    channel_breakdown: List[Dict[str, Any]] = Field(default_factory=list)
    daily_breakdown: List[Dict[str, Any]] = Field(default_factory=list)


class NotificationDeliveryResponse(BaseModel):
    """Schema for notification delivery response"""
    delivery_id: Optional[str] = None
    status: str
    message: str
    channels_targeted: Optional[int] = None
    recipient: Optional[str] = None
    subject: Optional[str] = None
    queued_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    estimated_delivery_time: Optional[datetime] = None
    last_error: Optional[str] = None
    tracking_url: Optional[str] = None
    channel_statuses: Optional[List[Dict[str, Any]]] = Field(default_factory=list)