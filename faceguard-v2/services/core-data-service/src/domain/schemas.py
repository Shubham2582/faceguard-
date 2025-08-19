"""
FACEGUARD V2 CORE DATA SERVICE - PYDANTIC SCHEMAS
Rule 2: Zero Placeholder Code - Real request/response validation
Rule 3: Error-First Development - Comprehensive field validation
"""

from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


class PersonBase(BaseModel):
    """Base person schema with common fields"""
    first_name: str = Field(..., min_length=1, max_length=100, description="Person's first name")
    last_name: str = Field(..., max_length=100, description="Person's last name")  # Removed min_length for V1 compatibility
    email: Optional[EmailStr] = Field(None, description="Email address")
    phone: Optional[str] = Field(None, max_length=20, description="Phone number")
    department: Optional[str] = Field(None, max_length=100, description="Department")
    position: Optional[str] = Field(None, max_length=100, description="Position/Role")
    access_level: str = Field(default="visitor", max_length=50, description="Access level")
    
    @validator('phone')
    def validate_phone(cls, v):
        if v and len(v.strip()) == 0:
            return None
        return v
    
    @validator('access_level')
    def validate_access_level(cls, v):
        # V1 Database ENUM values (must match exactly)
        allowed_levels = ["visitor", "employee", "contractor", "admin", "security", "vip"]
        if v not in allowed_levels:
            raise ValueError(f"Access level must be one of: {allowed_levels}")
        return v


class PersonCreate(PersonBase):
    """Schema for creating new persons"""
    person_id: Optional[str] = Field(None, max_length=255, description="Optional custom person ID")
    is_vip: bool = Field(default=False, description="VIP status")
    is_watchlist: bool = Field(default=False, description="Watchlist status")


class PersonUpdate(BaseModel):
    """Schema for updating persons - all fields optional"""
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)  # Removed min_length for V1 compatibility
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    department: Optional[str] = Field(None, max_length=100)
    position: Optional[str] = Field(None, max_length=100)
    access_level: Optional[str] = Field(None, max_length=50)
    is_vip: Optional[bool] = None
    is_watchlist: Optional[bool] = None
    status: Optional[str] = Field(None, max_length=50)
    
    @validator('status')
    def validate_status(cls, v):
        if v is not None:
            # V1 Database ENUM values (must match exactly)
            allowed_statuses = ["active", "inactive", "blocked", "pending", "archived"]
            if v not in allowed_statuses:
                raise ValueError(f"Status must be one of: {allowed_statuses}")
        return v


class PersonResponse(PersonBase):
    """Schema for person responses"""
    id: str
    person_id: str
    
    @validator('id', pre=True)
    def convert_uuid_to_string(cls, v):
        """Convert UUID objects to strings for V1 compatibility"""
        if hasattr(v, '__str__'):
            return str(v)
        return v
    status: str
    is_vip: bool
    is_watchlist: bool
    is_verified: bool
    
    # Metrics
    face_count: int
    embedding_count: int
    recognition_count: int
    
    # Quality metrics
    avg_confidence: Optional[Decimal]
    avg_face_quality: Optional[Decimal]
    best_face_quality: Optional[Decimal]
    
    # Timestamps
    first_seen: Optional[datetime]
    last_seen: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class PersonListResponse(BaseModel):
    """Schema for paginated person lists"""
    total: int = Field(..., description="Total number of persons")
    page: int = Field(..., description="Current page number")
    limit: int = Field(..., description="Items per page")
    persons: List[PersonResponse] = Field(..., description="List of persons")
    
    @validator('page')
    def validate_page(cls, v):
        if v < 1:
            raise ValueError("Page must be >= 1")
        return v
    
    @validator('limit')
    def validate_limit(cls, v):
        if not (1 <= v <= 100):
            raise ValueError("Limit must be between 1 and 100")
        return v


class EmbeddingBase(BaseModel):
    """Base embedding schema"""
    vector_data: List[float] = Field(..., description="512D embedding vector")
    confidence_score: Decimal = Field(..., ge=0.0, le=1.0, description="Confidence score")
    quality_score: Optional[Decimal] = Field(None, ge=0.0, le=1.0, description="Quality score")
    model_name: str = Field(default="buffalo_l", max_length=100, description="Model name")
    model_version: str = Field(default="1.0.0", max_length=50, description="Model version")
    
    @validator('vector_data')
    def validate_vector_dimension(cls, v):
        if len(v) != 512:
            raise ValueError("Vector must be exactly 512 dimensions")
        return v
    
    @validator('model_name')
    def validate_model_name(cls, v):
        allowed_models = ["buffalo_l", "arcface_r100", "arcface_r50"]
        if v not in allowed_models:
            raise ValueError(f"Model name must be one of: {allowed_models}")
        return v


class EmbeddingCreate(EmbeddingBase):
    """Schema for creating embeddings"""
    person_id: str = Field(..., description="Person UUID or person_id")
    embedding_id: Optional[str] = Field(None, max_length=255, description="Optional custom embedding ID")
    is_primary: bool = Field(default=False, description="Primary embedding flag")


class EmbeddingResponse(EmbeddingBase):
    """Schema for embedding responses"""
    id: str
    person_id: str
    embedding_id: str
    dimension: int
    status: str
    is_primary: bool
    is_template: bool
    is_verified: bool
    extracted_at: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class RecognitionEventCreate(BaseModel):
    """Schema for creating recognition events"""
    person_id: Optional[str] = Field(None, description="Recognized person ID")
    embedding_id: Optional[str] = Field(None, description="Matching embedding ID")
    confidence_score: Decimal = Field(..., ge=0.0, le=1.0, description="Recognition confidence")
    recognition_status: str = Field(..., description="Recognition result")
    camera_id: Optional[str] = Field(None, max_length=255, description="Camera identifier")
    location: Optional[str] = Field(None, max_length=255, description="Recognition location")
    processing_time_ms: Optional[int] = Field(None, ge=0, description="Processing time in milliseconds")
    
    @validator('recognition_status')
    def validate_recognition_status(cls, v):
        allowed_statuses = ["recognized", "unknown", "low_confidence", "failed"]
        if v not in allowed_statuses:
            raise ValueError(f"Recognition status must be one of: {allowed_statuses}")
        return v


class RecognitionEventResponse(RecognitionEventCreate):
    """Schema for recognition event responses"""
    id: str
    event_id: str
    model_used: str
    detected_at: datetime
    processed_at: datetime
    
    class Config:
        from_attributes = True


class ErrorResponse(BaseModel):
    """Standard error response schema"""
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[dict] = Field(None, description="Additional error details")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")


class SuccessResponse(BaseModel):
    """Standard success response schema"""
    success: bool = Field(default=True, description="Operation success flag")
    message: str = Field(..., description="Success message")
    data: Optional[dict] = Field(None, description="Response data")


# Person Sighting Schemas

class SightingBase(BaseModel):
    """Base sighting schema with common fields"""
    person_id: str = Field(..., description="Person UUID")
    camera_id: str = Field(..., description="Camera UUID")
    confidence_score: Decimal = Field(..., ge=0.0, le=1.0, description="Recognition confidence")
    source_type: str = Field(..., description="Source of sighting")
    
    @validator('source_type')
    def validate_source_type(cls, v):
        allowed_types = ["camera_stream", "image_upload", "video_upload"]
        if v not in allowed_types:
            raise ValueError(f"Source type must be one of: {allowed_types}")
        return v


class SightingCreate(SightingBase):
    """Schema for creating person sightings"""
    sighting_timestamp: Optional[datetime] = Field(None, description="Sighting timestamp (defaults to now)")
    source_metadata: Optional[dict] = Field(None, description="Source-specific metadata")
    cropped_image_path: Optional[str] = Field(None, max_length=500, description="Path to cropped face image")
    image_quality_score: Optional[Decimal] = Field(None, ge=0.0, le=1.0, description="Image quality score")
    face_bbox: Optional[List[float]] = Field(None, description="Face bounding box [x1,y1,x2,y2]")
    embedding_improved: bool = Field(default=False, description="Whether embedding was improved")


class SightingResponse(SightingBase):
    """Schema for sighting responses"""
    id: str
    sighting_timestamp: datetime
    source_metadata: Optional[dict]
    cropped_image_path: Optional[str]
    image_quality_score: Optional[Decimal]
    face_bbox: Optional[List[float]]
    embedding_improved: bool
    created_at: datetime
    
    # Related data (optional)
    person_name: Optional[str] = Field(None, description="Person name for convenience")
    camera_name: Optional[str] = Field(None, description="Camera name for convenience")
    
    @validator('id', pre=True)
    def convert_uuid_to_string(cls, v):
        """Convert UUID objects to strings"""
        if hasattr(v, '__str__'):
            return str(v)
        return v
    
    class Config:
        from_attributes = True


class SightingListResponse(BaseModel):
    """Schema for paginated sighting lists"""
    total: int = Field(..., description="Total number of sightings")
    page: int = Field(..., description="Current page number")
    limit: int = Field(..., description="Items per page")
    sightings: List[SightingResponse] = Field(..., description="List of sightings")
    
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


class SightingAnalytics(BaseModel):
    """Schema for sighting analytics"""
    total_sightings: int = Field(..., description="Total sightings in period")
    unique_persons: int = Field(..., description="Unique persons sighted")
    active_cameras: int = Field(..., description="Active cameras with sightings")
    avg_confidence: Optional[Decimal] = Field(None, description="Average confidence score")
    top_cameras: List[dict] = Field(default_factory=list, description="Top cameras by sighting count")
    top_persons: List[dict] = Field(default_factory=list, description="Most sighted persons")
    sightings_by_hour: List[dict] = Field(default_factory=list, description="Sightings distribution by hour")
    sightings_by_source: dict = Field(default_factory=dict, description="Sightings by source type")
    quality_distribution: dict = Field(default_factory=dict, description="Image quality distribution")
    period_start: datetime = Field(..., description="Analytics period start")
    period_end: datetime = Field(..., description="Analytics period end")


# Notification System Schemas

class NotificationChannelBase(BaseModel):
    """Base notification channel schema"""
    channel_name: str = Field(..., min_length=1, max_length=100, description="Channel name")
    channel_type: str = Field(..., description="Channel type")
    configuration: dict = Field(..., description="Channel-specific configuration")
    is_active: bool = Field(default=True, description="Channel active status")
    rate_limit_per_minute: int = Field(default=60, ge=1, le=1000, description="Rate limit per minute")
    
    @validator('channel_type')
    def validate_channel_type(cls, v):
        allowed_types = ["email", "sms", "webhook", "websocket", "slack", "discord", "teams"]
        if v not in allowed_types:
            raise ValueError(f"Channel type must be one of: {allowed_types}")
        return v


class NotificationChannelCreate(NotificationChannelBase):
    """Schema for creating notification channels"""
    pass


class NotificationChannelUpdate(BaseModel):
    """Schema for updating notification channels"""
    channel_name: Optional[str] = Field(None, min_length=1, max_length=100)
    channel_type: Optional[str] = None
    configuration: Optional[dict] = None
    is_active: Optional[bool] = None
    rate_limit_per_minute: Optional[int] = Field(None, ge=1, le=1000)
    
    @validator('channel_type')
    def validate_channel_type(cls, v):
        if v is not None:
            allowed_types = ["email", "sms", "webhook", "websocket", "slack", "discord", "teams"]
            if v not in allowed_types:
                raise ValueError(f"Channel type must be one of: {allowed_types}")
        return v


class NotificationChannelResponse(NotificationChannelBase):
    """Schema for notification channel responses"""
    id: str
    created_at: datetime
    updated_at: Optional[datetime]
    
    @validator('id', pre=True)
    def convert_uuid_to_string(cls, v):
        if hasattr(v, '__str__'):
            return str(v)
        return v
    
    class Config:
        from_attributes = True


class AlertRuleBase(BaseModel):
    """Base alert rule schema"""
    rule_name: str = Field(..., min_length=1, max_length=200, description="Rule name")
    description: Optional[str] = Field(None, max_length=500, description="Rule description")
    trigger_conditions: dict = Field(..., description="Trigger conditions as JSON")
    priority: str = Field(default="medium", description="Alert priority")
    cooldown_minutes: int = Field(default=30, ge=0, le=1440, description="Cooldown in minutes")
    notification_channels: List[str] = Field(..., description="List of channel IDs")
    message_template: Optional[str] = Field(None, max_length=1000, description="Message template")
    is_active: bool = Field(default=True, description="Rule active status")
    
    @validator('priority')
    def validate_priority(cls, v):
        allowed_priorities = ["low", "medium", "high", "critical"]
        if v not in allowed_priorities:
            raise ValueError(f"Priority must be one of: {allowed_priorities}")
        return v


class AlertRuleCreate(AlertRuleBase):
    """Schema for creating alert rules"""
    pass


class AlertRuleUpdate(BaseModel):
    """Schema for updating alert rules"""
    rule_name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=500)
    trigger_conditions: Optional[dict] = None
    priority: Optional[str] = None
    cooldown_minutes: Optional[int] = Field(None, ge=0, le=1440)
    notification_channels: Optional[List[str]] = None
    message_template: Optional[str] = Field(None, max_length=1000)
    is_active: Optional[bool] = None
    
    @validator('priority')
    def validate_priority(cls, v):
        if v is not None:
            allowed_priorities = ["low", "medium", "high", "critical"]
            if v not in allowed_priorities:
                raise ValueError(f"Priority must be one of: {allowed_priorities}")
        return v


class AlertRuleResponse(AlertRuleBase):
    """Schema for alert rule responses"""
    id: str
    created_at: datetime
    updated_at: Optional[datetime]
    
    @validator('id', pre=True)
    def convert_uuid_to_string(cls, v):
        if hasattr(v, '__str__'):
            return str(v)
        return v
    
    @validator('notification_channels', pre=True)
    def convert_notification_channels_to_strings(cls, v):
        """Convert UUID array to string array for API response"""
        if isinstance(v, list):
            return [str(channel_id) for channel_id in v]
        elif isinstance(v, str) and v.startswith('{') and v.endswith('}'):
            # Handle PostgreSQL array format like '{uuid1,uuid2}'
            import re
            uuids = re.findall(r'[0-9a-f-]{36}', v)
            return uuids
        return v
    
    class Config:
        from_attributes = True


class AlertRuleListResponse(BaseModel):
    """Schema for paginated alert rule lists"""
    total: int = Field(..., description="Total number of alert rules")
    page: int = Field(..., description="Current page number")
    limit: int = Field(..., description="Items per page")
    alert_rules: List[AlertRuleResponse] = Field(..., description="List of alert rules")


class NotificationLogBase(BaseModel):
    """Base notification log schema"""
    subject: Optional[str] = Field(None, max_length=200, description="Notification subject")
    message: str = Field(..., min_length=1, max_length=5000, description="Notification message")
    recipient: str = Field(..., min_length=1, max_length=255, description="Recipient identifier")
    priority: str = Field(default="medium", description="Notification priority")
    delivery_options: Optional[dict] = Field(None, description="Delivery options")
    
    @validator('priority')
    def validate_priority(cls, v):
        allowed_priorities = ["low", "medium", "high", "critical"]
        if v not in allowed_priorities:
            raise ValueError(f"Priority must be one of: {allowed_priorities}")
        return v


class NotificationLogCreate(NotificationLogBase):
    """Schema for creating notification logs"""
    alert_id: Optional[str] = Field(None, description="Associated alert ID")
    channel_id: str = Field(..., description="Notification channel ID")
    delivery_id: Optional[str] = Field(None, max_length=255, description="External delivery ID")


class NotificationLogResponse(BaseModel):
    """Schema for notification log responses - adapted for database schema"""
    id: str
    alert_id: Optional[str]
    channel_id: str
    delivery_id: Optional[str] = Field(None, description="External delivery ID")
    delivery_status: str
    error_message: Optional[str]
    retry_count: int
    created_at: datetime
    sent_at: Optional[datetime]
    delivered_at: Optional[datetime]
    updated_at: Optional[datetime]
    
    # Optional fields extracted from delivery_metadata JSONB
    subject: Optional[str] = Field(None, description="Notification subject")
    message: Optional[str] = Field(None, description="Notification message")
    recipient: Optional[str] = Field(None, description="Recipient identifier")
    priority: Optional[str] = Field("medium", description="Notification priority")
    
    @validator('id', pre=True)
    def convert_uuid_to_string(cls, v):
        if hasattr(v, '__str__'):
            return str(v)
        return v
    
    @validator('alert_id', pre=True)
    def convert_alert_id_to_string(cls, v):
        if v and hasattr(v, '__str__'):
            return str(v)
        return v
    
    @validator('channel_id', pre=True)
    def convert_channel_id_to_string(cls, v):
        if hasattr(v, '__str__'):
            return str(v)
        return v
    
    class Config:
        from_attributes = True


class NotificationLogListResponse(BaseModel):
    """Schema for paginated notification log lists"""
    total: int = Field(..., description="Total number of notification logs")
    page: int = Field(..., description="Current page number")
    limit: int = Field(..., description="Items per page")
    logs: List[NotificationLogResponse] = Field(..., description="List of notification logs")


class NotificationAnalytics(BaseModel):
    """Schema for notification analytics"""
    total_notifications: int = Field(..., description="Total notifications sent")
    successful_deliveries: int = Field(..., description="Successful deliveries")
    failed_deliveries: int = Field(..., description="Failed deliveries")
    pending_deliveries: int = Field(..., description="Pending deliveries")
    success_rate: Optional[Decimal] = Field(None, description="Success rate percentage")
    active_channels: int = Field(..., description="Active notification channels")
    total_alert_rules: int = Field(..., description="Total alert rules")
    active_alert_rules: int = Field(..., description="Active alert rules")
    alerts_triggered_today: int = Field(..., description="Alerts triggered today")
    top_channels: List[dict] = Field(default_factory=list, description="Top channels by volume")
    notifications_by_priority: dict = Field(default_factory=dict, description="Notifications by priority")
    notifications_by_hour: List[dict] = Field(default_factory=list, description="Notifications by hour")
    period_start: datetime = Field(..., description="Analytics period start")
    period_end: datetime = Field(..., description="Analytics period end")


# High Priority Person Schemas

class HighPriorityPersonCreate(BaseModel):
    """Schema for creating a high priority person"""
    person_id: str = Field(..., description="UUID of the person to add to high priority list")
    priority_level: str = Field(default="high", description="Priority level: high, critical, wanted")
    alert_reason: Optional[str] = Field(None, description="Reason why this person is high priority")
    added_by: str = Field(..., description="Username/ID of who is adding this person")
    escalation_channels: str = Field(default="sms,email,dashboard", description="Comma-separated list of channels")
    notification_frequency: str = Field(default="immediate", description="immediate, daily, weekly")


class HighPriorityPersonUpdate(BaseModel):
    """Schema for updating a high priority person"""
    priority_level: Optional[str] = Field(None, description="Priority level: high, critical, wanted")
    alert_reason: Optional[str] = Field(None, description="Reason why this person is high priority")
    escalation_channels: Optional[str] = Field(None, description="Comma-separated list of channels")
    notification_frequency: Optional[str] = Field(None, description="immediate, daily, weekly")
    is_active: Optional[bool] = Field(None, description="Active status")


class HighPriorityPersonRemove(BaseModel):
    """Schema for removing a person from high priority list"""
    removed_by: str = Field(..., description="Username/ID of who is removing this person")
    removal_reason: Optional[str] = Field(None, description="Reason for removal")


class HighPriorityPersonResponse(BaseModel):
    """Schema for high priority person response"""
    id: str
    person_id: str
    priority_level: str
    alert_reason: Optional[str]
    added_by: str
    added_at: datetime
    last_updated: datetime
    is_active: bool
    removed_at: Optional[datetime]
    removed_by: Optional[str]
    removal_reason: Optional[str]
    escalation_channels: str
    notification_frequency: str
    
    # Person details (from relationship)
    person_first_name: Optional[str] = None
    person_last_name: Optional[str] = None
    person_person_id: Optional[str] = None

    @validator('id', pre=True)
    def convert_uuid_to_string(cls, v):
        if hasattr(v, '__str__'):
            return str(v)
        return v
    
    @validator('person_id', pre=True)
    def convert_person_id_to_string(cls, v):
        if hasattr(v, '__str__'):
            return str(v)
        return v

    class Config:
        from_attributes = True


class HighPriorityPersonListResponse(BaseModel):
    """Schema for paginated high priority persons list"""
    high_priority_persons: List[HighPriorityPersonResponse]
    total: int
    page: int
    limit: int
    pages: int


class HighPriorityCheckResponse(BaseModel):
    """Schema for checking if a person is high priority"""
    person_id: str
    is_high_priority: bool
    priority_level: Optional[str] = None
    alert_reason: Optional[str] = None
    escalation_channels: Optional[str] = None
    notification_frequency: Optional[str] = None
    added_by: Optional[str] = None
    added_at: Optional[datetime] = None

    @validator('person_id', pre=True)
    def convert_person_id_to_string(cls, v):
        if hasattr(v, '__str__'):
            return str(v)
        return v


# Notification Contact Schemas

class NotificationContactBase(BaseModel):
    """Base notification contact schema"""
    contact_name: str = Field(..., min_length=1, max_length=100, description="Contact name")
    contact_type: str = Field(..., description="Contact type: email, phone, webhook")
    contact_value: str = Field(..., min_length=1, max_length=255, description="Contact value (email/phone/URL)")
    description: Optional[str] = Field(None, description="Contact description")
    tags: Optional[str] = Field(None, max_length=200, description="Comma-separated tags")
    priority: str = Field(default="medium", description="Contact priority")
    notification_hours: Optional[str] = Field(None, max_length=100, description="Notification hours (e.g., 09:00-17:00)")
    notification_days: Optional[str] = Field(None, max_length=50, description="Notification days (e.g., mon,tue,wed,thu,fri)")
    max_notifications_per_hour: int = Field(default=10, ge=1, le=100, description="Max notifications per hour")
    
    @validator('contact_type')
    def validate_contact_type(cls, v):
        allowed_types = ["email", "phone", "webhook"]
        if v not in allowed_types:
            raise ValueError(f"Contact type must be one of: {allowed_types}")
        return v
    
    @validator('priority')
    def validate_priority(cls, v):
        allowed_priorities = ["low", "medium", "high", "critical"]
        if v not in allowed_priorities:
            raise ValueError(f"Priority must be one of: {allowed_priorities}")
        return v
    
    @validator('contact_value')
    def validate_contact_value(cls, v, values):
        """Validate contact value based on type"""
        contact_type = values.get('contact_type')
        if contact_type == 'email':
            # Basic email validation
            if '@' not in v or '.' not in v:
                raise ValueError("Invalid email format")
        elif contact_type == 'phone':
            # Basic phone validation (allow digits, +, -, (), spaces)
            import re
            if not re.match(r'^[\d\s\+\-\(\)]+$', v):
                raise ValueError("Invalid phone format")
        elif contact_type == 'webhook':
            # Basic URL validation
            if not (v.startswith('http://') or v.startswith('https://')):
                raise ValueError("Webhook must be a valid HTTP/HTTPS URL")
        return v


class NotificationContactCreate(NotificationContactBase):
    """Schema for creating notification contacts"""
    person_id: Optional[str] = Field(None, description="Link to specific person (UUID)")
    added_by: str = Field(..., description="Username/ID of who is adding this contact")
    is_primary: bool = Field(default=False, description="Mark as primary contact")
    is_active: bool = Field(default=True, description="Contact active status")


class NotificationContactUpdate(BaseModel):
    """Schema for updating notification contacts"""
    contact_name: Optional[str] = Field(None, min_length=1, max_length=100)
    contact_value: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    tags: Optional[str] = Field(None, max_length=200)
    priority: Optional[str] = None
    notification_hours: Optional[str] = Field(None, max_length=100)
    notification_days: Optional[str] = Field(None, max_length=50)
    max_notifications_per_hour: Optional[int] = Field(None, ge=1, le=100)
    is_primary: Optional[bool] = None
    is_active: Optional[bool] = None
    
    @validator('priority')
    def validate_priority(cls, v):
        if v is not None:
            allowed_priorities = ["low", "medium", "high", "critical"]
            if v not in allowed_priorities:
                raise ValueError(f"Priority must be one of: {allowed_priorities}")
        return v


class NotificationContactVerify(BaseModel):
    """Schema for verifying notification contacts"""
    verification_code: str = Field(..., min_length=4, max_length=20, description="Verification code")


class NotificationContactResponse(NotificationContactBase):
    """Schema for notification contact responses"""
    id: str
    person_id: Optional[str]
    is_primary: bool
    is_verified: bool
    verified_at: Optional[datetime]
    is_active: bool
    last_notification_sent: Optional[datetime]
    total_notifications_sent: int
    failed_attempts: int
    added_by: str
    added_at: datetime
    updated_at: Optional[datetime]
    
    # Related person info (optional)
    person_name: Optional[str] = Field(None, description="Person name if linked")
    
    @validator('id', pre=True)
    def convert_uuid_to_string(cls, v):
        if hasattr(v, '__str__'):
            return str(v)
        return v
    
    @validator('person_id', pre=True)
    def convert_person_id_to_string(cls, v):
        if v and hasattr(v, '__str__'):
            return str(v)
        return v
    
    class Config:
        from_attributes = True


class NotificationContactListResponse(BaseModel):
    """Schema for paginated notification contact lists"""
    total: int = Field(..., description="Total number of contacts")
    page: int = Field(..., description="Current page number")
    limit: int = Field(..., description="Items per page")
    contacts: List[NotificationContactResponse] = Field(..., description="List of contacts")
    
    @validator('page')
    def validate_page(cls, v):
        if v < 1:
            raise ValueError("Page must be >= 1")
        return v
    
    @validator('limit')
    def validate_limit(cls, v):
        if not (1 <= v <= 100):
            raise ValueError("Limit must be between 1 and 100")
        return v


class NotificationContactTestRequest(BaseModel):
    """Schema for testing a notification contact"""
    test_message: str = Field(default="This is a test notification from FaceGuard V2", description="Test message to send")
    test_subject: Optional[str] = Field(default="FaceGuard V2 Test Notification", description="Test subject (for emails)")


class NotificationContactTestResponse(BaseModel):
    """Schema for notification contact test response"""
    contact_id: str
    contact_type: str
    contact_value: str
    test_status: str  # success, failed
    test_message: str
    delivery_response: Optional[dict] = None
    error_message: Optional[str] = None
    tested_at: datetime


