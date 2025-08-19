"""
Domain models for Camera Stream Service
Following FACEGUARD_V2_STRATEGIC_IMPLEMENTATION_GUIDE.md domain layer architecture
"""
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
import uuid


class CameraStatus(str, Enum):
    """Camera connection status"""
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    ERROR = "error"
    INACTIVE = "inactive"


class CameraType(str, Enum):
    """Camera source type"""
    USB = "usb"
    IP = "ip"
    RTSP = "rtsp"
    FILE = "file"


class StreamStatus(str, Enum):
    """Stream processing status"""
    ACTIVE = "active"
    PAUSED = "paused"
    STOPPED = "stopped"
    ERROR = "error"


class FrameQuality(str, Enum):
    """Frame quality assessment"""
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    UNUSABLE = "unusable"


# ==================== CAMERA MODELS ====================

class CameraConfiguration(BaseModel):
    """Camera configuration model"""
    camera_id: str = Field(..., description="Unique camera identifier")
    source: str = Field(..., description="Camera source (USB index or URL)")
    camera_type: CameraType = Field(..., description="Camera type")
    name: str = Field(..., description="Camera display name")
    location: Optional[str] = Field(None, description="Camera location")
    resolution_width: int = Field(1280, ge=320, le=1920, description="Frame width")
    resolution_height: int = Field(720, ge=240, le=1080, description="Frame height")
    frame_rate: int = Field(2, ge=1, le=30, description="Target frame rate")
    enabled: bool = Field(True, description="Camera enabled status")
    auto_reconnect: bool = Field(True, description="Auto-reconnect on failure")
    reconnect_attempts: int = Field(3, ge=1, le=10, description="Max reconnect attempts")
    reconnect_delay: int = Field(5, ge=1, le=60, description="Reconnect delay seconds")
    
    class Config:
        use_enum_values = True


class CameraInfo(BaseModel):
    """Camera information and status"""
    camera_id: str = Field(..., description="Camera identifier")
    configuration: CameraConfiguration = Field(..., description="Camera configuration")
    status: CameraStatus = Field(..., description="Current status")
    stream_status: StreamStatus = Field(..., description="Stream status")
    last_frame_time: Optional[datetime] = Field(None, description="Last frame timestamp")
    frames_processed: int = Field(0, ge=0, description="Total frames processed")
    frames_recognized: int = Field(0, ge=0, description="Frames with recognition")
    errors_count: int = Field(0, ge=0, description="Error count")
    last_error: Optional[str] = Field(None, description="Last error message")
    uptime_seconds: int = Field(0, ge=0, description="Uptime in seconds")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation time")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update time")
    
    class Config:
        use_enum_values = True


# ==================== FRAME MODELS ====================

class FrameMetadata(BaseModel):
    """Frame metadata and quality information"""
    frame_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Frame identifier")
    camera_id: str = Field(..., description="Source camera ID")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Frame timestamp")
    frame_number: int = Field(..., ge=0, description="Frame sequence number")
    width: int = Field(..., ge=1, description="Frame width")
    height: int = Field(..., ge=1, description="Frame height")
    channels: int = Field(3, ge=1, le=4, description="Color channels")
    file_size: int = Field(..., ge=0, description="Frame size in bytes")
    quality_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Quality score")
    quality_grade: Optional[FrameQuality] = Field(None, description="Quality grade")
    blur_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Blur assessment")
    brightness_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Brightness score")
    
    class Config:
        use_enum_values = True


class ProcessedFrame(BaseModel):
    """Processed frame with recognition results"""
    metadata: FrameMetadata = Field(..., description="Frame metadata")
    faces_detected: int = Field(0, ge=0, description="Number of faces detected")
    faces_recognized: int = Field(0, ge=0, description="Number of faces recognized")
    processing_time_ms: float = Field(..., ge=0, description="Processing time in milliseconds")
    recognition_results: List[Dict[str, Any]] = Field(default_factory=list, description="Recognition results")
    cache_hit: bool = Field(False, description="Whether recognition was cached")
    error: Optional[str] = Field(None, description="Processing error")
    
    class Config:
        use_enum_values = True


# ==================== EVENT MODELS ====================

class RecognitionEventType(str, Enum):
    """Recognition event types"""
    PERSON_DETECTED = "person_detected"
    PERSON_RECOGNIZED = "person_recognized"
    UNKNOWN_PERSON = "unknown_person"
    MULTIPLE_FACES = "multiple_faces"
    NO_FACES = "no_faces"
    PROCESSING_ERROR = "processing_error"


class RecognitionEvent(BaseModel):
    """Recognition event for publishing"""
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Event identifier")
    event_type: RecognitionEventType = Field(..., description="Event type")
    camera_id: str = Field(..., description="Source camera")
    frame_id: str = Field(..., description="Source frame")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Event timestamp")
    person_id: Optional[str] = Field(None, description="Recognized person ID")
    person_name: Optional[str] = Field(None, description="Recognized person name")
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0, description="Recognition confidence")
    faces_detected: int = Field(0, ge=0, description="Total faces detected")
    location: Optional[str] = Field(None, description="Camera location")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    class Config:
        use_enum_values = True


# ==================== SERVICE MODELS ====================

class ServiceHealth(BaseModel):
    """Service health information"""
    status: str = Field(..., description="Overall service status")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Health check timestamp")
    uptime_seconds: int = Field(..., ge=0, description="Service uptime")
    cameras_total: int = Field(..., ge=0, description="Total cameras configured")
    cameras_active: int = Field(..., ge=0, description="Active cameras")
    cameras_connected: int = Field(..., ge=0, description="Connected cameras")
    frames_processed_total: int = Field(..., ge=0, description="Total frames processed")
    events_published_total: int = Field(..., ge=0, description="Total events published")
    memory_usage_mb: float = Field(..., ge=0, description="Memory usage in MB")
    cpu_usage_percent: float = Field(..., ge=0, le=100, description="CPU usage percentage")
    errors_count: int = Field(..., ge=0, description="Total errors")
    
    class Config:
        use_enum_values = True


class ServiceStats(BaseModel):
    """Detailed service statistics"""
    service_name: str = Field(..., description="Service name")
    version: str = Field(..., description="Service version")
    start_time: datetime = Field(..., description="Service start time")
    current_time: datetime = Field(default_factory=datetime.utcnow, description="Current time")
    cameras: List[CameraInfo] = Field(default_factory=list, description="Camera information")
    processing_stats: Dict[str, Any] = Field(default_factory=dict, description="Processing statistics")
    event_stats: Dict[str, Any] = Field(default_factory=dict, description="Event statistics")
    performance_metrics: Dict[str, Any] = Field(default_factory=dict, description="Performance metrics")
    
    class Config:
        use_enum_values = True


# ==================== REQUEST/RESPONSE MODELS ====================

class CameraCreateRequest(BaseModel):
    """Camera creation request"""
    source: str = Field(..., description="Camera source")
    name: str = Field(..., description="Camera name")
    location: Optional[str] = Field(None, description="Camera location")
    resolution_width: int = Field(1280, ge=320, le=1920)
    resolution_height: int = Field(720, ge=240, le=1080)
    frame_rate: int = Field(2, ge=1, le=30)
    enabled: bool = Field(True, description="Enable camera")


class CameraUpdateRequest(BaseModel):
    """Camera update request"""
    name: Optional[str] = Field(None, description="Camera name")
    location: Optional[str] = Field(None, description="Camera location")
    resolution_width: Optional[int] = Field(None, ge=320, le=1920)
    resolution_height: Optional[int] = Field(None, ge=240, le=1080)
    frame_rate: Optional[int] = Field(None, ge=1, le=30)
    enabled: Optional[bool] = Field(None, description="Enable/disable camera")


class StreamControlRequest(BaseModel):
    """Stream control request"""
    action: str = Field(..., description="Control action: start, stop, pause, resume")
    camera_ids: Optional[List[str]] = Field(None, description="Specific camera IDs (all if None)")


class EventSubscribeRequest(BaseModel):
    """Event subscription request"""
    channels: List[str] = Field(..., description="Event channels to subscribe")
    filter_camera_ids: Optional[List[str]] = Field(None, description="Filter by camera IDs")
    filter_event_types: Optional[List[RecognitionEventType]] = Field(None, description="Filter by event types")


# ==================== ERROR MODELS ====================

class ServiceError(BaseModel):
    """Service error information"""
    error_code: str = Field(..., description="Error code")
    error_message: str = Field(..., description="Error message")
    error_details: Optional[Dict[str, Any]] = Field(None, description="Error details")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")
    component: str = Field(..., description="Component that generated error")
    camera_id: Optional[str] = Field(None, description="Related camera ID")
    
    class Config:
        use_enum_values = True