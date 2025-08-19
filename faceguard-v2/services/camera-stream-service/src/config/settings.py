"""
Camera Stream Service Configuration
Following FACEGUARD_V2_STRATEGIC_IMPLEMENTATION_GUIDE.md configuration management strategy
"""
from pydantic_settings import BaseSettings
from pydantic import Field, validator
from typing import List, Optional
import os


class Settings(BaseSettings):
    """Camera Stream Service Configuration with validation"""
    
    # Service Configuration
    service_host: str = Field(default="0.0.0.0", description="Service bind host")
    service_port: int = Field(default=8003, ge=1024, le=65535, description="Service port")
    service_version: str = Field(default="2.0.0", description="Service version")
    service_name: str = Field(default="camera-stream-service", description="Service name")
    log_level: str = Field(default="INFO", description="Logging level")
    
    # Camera Configuration
    camera_sources: List[str] = Field(default=["0"], description="Camera sources (USB index or RTSP URLs)")
    camera_frame_rate: int = Field(default=2, ge=1, le=30, description="Frame extraction rate (FPS)")
    camera_resolution_width: int = Field(default=1280, ge=320, le=1920, description="Camera width")
    camera_resolution_height: int = Field(default=720, ge=240, le=1080, description="Camera height")
    camera_reconnect_attempts: int = Field(default=3, ge=1, le=10, description="Reconnection attempts")
    camera_reconnect_delay: int = Field(default=5, ge=1, le=60, description="Reconnection delay (seconds)")
    camera_health_check_interval: int = Field(default=30, ge=5, le=300, description="Health check interval")
    
    # Frame Processing Configuration
    frame_quality_threshold: float = Field(default=0.5, ge=0.0, le=1.0, description="Minimum frame quality")
    frame_buffer_size: int = Field(default=10, ge=1, le=100, description="Frame buffer size")
    frame_processing_timeout: int = Field(default=30, ge=5, le=120, description="Processing timeout")
    enable_frame_quality_assessment: bool = Field(default=True, description="Enable quality assessment")
    
    # Service Integration
    core_data_service_url: str = Field(default="http://localhost:8001", description="Core Data Service URL")
    face_recognition_service_url: str = Field(default="http://localhost:8002", description="Face Recognition Service URL")
    integration_timeout: int = Field(default=10, ge=1, le=60, description="Integration timeout")
    integration_retry_attempts: int = Field(default=3, ge=1, le=10, description="Integration retry attempts")
    
    # Event System Configuration
    redis_host: str = Field(default="localhost", description="Redis host")
    redis_port: int = Field(default=6379, ge=1, le=65535, description="Redis port")
    redis_db: int = Field(default=0, ge=0, le=15, description="Redis database")
    event_channel: str = Field(default="face_recognition_events", description="Event channel name")
    enable_event_persistence: bool = Field(default=True, description="Enable event persistence")
    event_batch_size: int = Field(default=100, ge=1, le=1000, description="Event batch size")
    
    # Performance Configuration
    max_concurrent_cameras: int = Field(default=4, ge=1, le=16, description="Max concurrent cameras")
    processing_queue_size: int = Field(default=50, ge=10, le=500, description="Processing queue size")
    memory_limit_mb: int = Field(default=512, ge=128, le=2048, description="Memory limit (MB)")
    enable_performance_monitoring: bool = Field(default=True, description="Enable performance monitoring")
    
    # Feature Flags (ALL ENABLED - following prevention rules)
    enable_multi_camera: bool = Field(default=True, description="Enable multiple cameras")
    enable_frame_quality_check: bool = Field(default=True, description="Enable frame quality checks")
    enable_event_publishing: bool = Field(default=True, description="Enable event publishing")
    enable_health_monitoring: bool = Field(default=True, description="Enable health monitoring")
    enable_analytics: bool = Field(default=True, description="Enable analytics")
    
    @validator('log_level')
    def validate_log_level(cls, v):
        """Validate log level"""
        allowed = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in allowed:
            raise ValueError(f'Log level must be one of: {allowed}')
        return v.upper()
    
    @validator('camera_sources', pre=True)
    def parse_camera_sources(cls, v):
        """Parse camera sources from string, int, or list"""
        if isinstance(v, (str, int)):
            # Convert to string first, then split
            v_str = str(v)
            return [source.strip() for source in v_str.split(',') if source.strip()]
        if isinstance(v, list):
            # Ensure all items are strings
            return [str(item) for item in v]
        return v
    
    @property
    def redis_url(self) -> str:
        """Construct Redis URL"""
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"
    
    @property
    def camera_resolution(self) -> tuple:
        """Get camera resolution as tuple"""
        return (self.camera_resolution_width, self.camera_resolution_height)
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get settings instance"""
    return settings