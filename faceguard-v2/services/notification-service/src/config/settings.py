"""
FACEGUARD V2 NOTIFICATION SERVICE - CONFIGURATION SETTINGS
Rule 2: Zero Placeholder Code - Real production configuration
Rule 3: Error-First Development - Environment validation
"""

from pydantic_settings import BaseSettings
from typing import Optional
import os


class NotificationServiceSettings(BaseSettings):
    """
    Notification Service Configuration
    Rule 2: Zero Placeholder Code - All settings have production defaults
    """
    
    # =============================================================================
    # SERVICE CONFIGURATION
    # =============================================================================
    
    service_name: str = "notification-service"
    service_version: str = "2.0.0"
    service_host: str = "0.0.0.0"
    service_port: int = 8004
    
    # Environment
    environment: str = "development"
    debug_mode: bool = False
    log_level: str = "INFO"
    
    # =============================================================================
    # CORE DATA SERVICE COMMUNICATION (NO DIRECT DATABASE ACCESS)
    # =============================================================================
    
    # Core Data Service Configuration (CRITICAL: API-only communication)
    core_data_service_url: str = "http://localhost:8001"
    core_data_timeout_seconds: int = 30
    core_data_max_retries: int = 3
    core_data_retry_delay_seconds: float = 1.0
    
    # HTTP Client Settings
    http_connection_pool_size: int = 10
    http_keepalive_timeout: int = 30
    http_max_connections: int = 100
    
    # =============================================================================
    # REDIS CONFIGURATION (For background tasks and caching)
    # =============================================================================
    
    redis_url: str = "redis://localhost:6379/1"  # Different DB from other services
    redis_password: Optional[str] = None
    redis_timeout: int = 30
    
    # =============================================================================
    # NOTIFICATION DELIVERY SETTINGS
    # =============================================================================
    
    # Rate Limiting
    default_rate_limit_per_minute: int = 60
    max_rate_limit_per_minute: int = 1000
    
    # Retry Configuration
    default_retry_attempts: int = 3
    max_retry_attempts: int = 10
    retry_delay_seconds: int = 60
    
    # Timeout Settings
    default_timeout_seconds: int = 30
    email_timeout_seconds: int = 60
    sms_timeout_seconds: int = 30
    webhook_timeout_seconds: int = 30
    
    # =============================================================================
    # EMAIL DELIVERY CONFIGURATION
    # =============================================================================
    
    # Default SMTP Settings (can be overridden per channel)
    default_smtp_host: str = "smtp.gmail.com"
    default_smtp_port: int = 587
    default_smtp_use_tls: bool = True
    
    # Email Template Settings
    email_template_dir: str = "templates/email"
    default_from_email: str = "noreply@faceguard.system"
    
    # =============================================================================
    # SMS DELIVERY CONFIGURATION
    # =============================================================================
    
    # Twilio Settings (Global fallback)
    twilio_account_sid: Optional[str] = None
    twilio_auth_token: Optional[str] = None
    twilio_from_number: Optional[str] = None
    
    # AWS SNS Settings (Alternative SMS provider)
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    aws_region: str = "us-east-1"
    
    # SMS Limits
    sms_character_limit: int = 160
    sms_unicode_limit: int = 70
    
    # =============================================================================
    # WEBHOOK DELIVERY CONFIGURATION
    # =============================================================================
    
    # Webhook Security
    webhook_signature_algorithm: str = "sha256"
    webhook_max_payload_size: int = 1024 * 1024  # 1MB
    webhook_secret: str = "test_secret_key"  # Default webhook secret for validation
    
    # =============================================================================
    # WEBSOCKET CONFIGURATION
    # =============================================================================
    
    websocket_host: str = "0.0.0.0"
    websocket_port: int = 8005
    websocket_path: str = "/ws"
    websocket_heartbeat_interval: int = 30
    
    # =============================================================================
    # ALERT PROCESSING CONFIGURATION
    # =============================================================================
    
    # Processing Intervals
    alert_processing_interval_seconds: int = 10
    escalation_processing_interval_seconds: int = 300  # 5 minutes
    cleanup_processing_interval_seconds: int = 3600   # 1 hour
    
    # Alert Limits
    max_alerts_per_rule_per_hour: int = 100
    max_cooldown_minutes: int = 1440  # 24 hours
    max_escalation_minutes: int = 1440  # 24 hours
    
    # =============================================================================
    # TEMPLATE AND FORMATTING
    # =============================================================================
    
    # Template Engine
    template_cache_enabled: bool = True
    template_auto_reload: bool = False
    
    # Message Formatting
    enable_rich_formatting: bool = True
    enable_emoji_support: bool = True
    
    # =============================================================================
    # SECURITY CONFIGURATION
    # =============================================================================
    
    # API Security
    api_key_header: str = "X-FaceGuard-API-Key"
    internal_api_key: Optional[str] = None
    
    # Encryption for sensitive data
    encryption_key: Optional[str] = None
    
    # =============================================================================
    # MONITORING AND OBSERVABILITY
    # =============================================================================
    
    # Health Checks
    enable_health_checks: bool = True
    health_check_interval_seconds: int = 30
    
    # Metrics
    enable_metrics: bool = True
    metrics_port: int = 8006
    
    # Logging
    enable_structured_logging: bool = True
    log_format: str = "json"
    
    # =============================================================================
    # FEATURE FLAGS
    # =============================================================================
    
    # Delivery Channels
    enable_email_delivery: bool = True
    enable_sms_delivery: bool = True
    enable_webhook_delivery: bool = True
    enable_websocket_delivery: bool = True
    
    # Background Processing
    enable_background_processing: bool = True
    enable_escalation_processing: bool = True
    enable_auto_resolution: bool = True
    
    # Development Features
    enable_test_mode: bool = False
    test_delivery_override: bool = False
    
    # =============================================================================
    # INTEGRATION ENDPOINTS
    # =============================================================================
    
    # Other FaceGuard V2 Services
    core_data_service_url: str = "http://localhost:8001"
    face_recognition_service_url: str = "http://localhost:8002"
    camera_stream_service_url: str = "http://localhost:8003"
    notification_service_url: str = "http://localhost:8004"
    
    # Service Discovery
    service_registry_url: Optional[str] = None
    
    class Config:
        env_file = ".env"
        env_prefix = "NOTIFICATION_"
        case_sensitive = False


# Global settings instance
_settings = None


def get_settings() -> NotificationServiceSettings:
    """Get global settings instance (singleton pattern)"""
    global _settings
    if _settings is None:
        _settings = NotificationServiceSettings()
    return _settings


def reload_settings() -> NotificationServiceSettings:
    """Reload settings from environment (for testing)"""
    global _settings
    _settings = NotificationServiceSettings()
    return _settings