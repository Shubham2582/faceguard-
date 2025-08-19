"""
FACEGUARD V2 CORE DATA SERVICE - DOMAIN MODELS
Rule 2: Zero Placeholder Code - Real SQLAlchemy models for V1 compatibility
Critical: Preserve 54 persons + 157 embeddings from V1 system
"""

from sqlalchemy import Column, String, Integer, DateTime, Boolean, DECIMAL, ForeignKey, ARRAY, Enum, Float
from sqlalchemy.dialects.postgresql import UUID, ARRAY as PG_ARRAY, JSONB, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import uuid
import enum

from storage.database import Base

# V1 Database ENUM Types (must match exactly)
class AccessLevel(enum.Enum):
    visitor = "visitor"
    employee = "employee"
    contractor = "contractor"
    admin = "admin"
    security = "security"
    vip = "vip"

class PersonStatus(enum.Enum):
    active = "active"
    inactive = "inactive"
    blocked = "blocked"
    pending = "pending"
    archived = "archived"


class PersonModel(Base):
    """
    Person model - EXACTLY matches V1 schema for data preservation
    Critical: confidence_score column (NOT extraction_confidence)
    """
    __tablename__ = "persons"
    
    # Primary Keys
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    person_id = Column(String(255), unique=True, nullable=False, index=True)
    
    # Personal Information
    first_name = Column(String(100), nullable=True)  # V1 allows null
    last_name = Column(String(100), nullable=True)   # V1 allows null
    full_name = Column(String(200), nullable=True)   # V1 has this column
    email = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)        # V1 uses varchar(50)
    
    # Organization Information
    department = Column(String(100), nullable=True)
    position = Column(String(100), nullable=True)
    employee_id = Column(String(50), nullable=True)  # V1 has this column
    access_level = Column(Enum(AccessLevel, name="accesslevel"), default=AccessLevel.visitor)
    person_metadata = Column(JSONB, nullable=True)   # V1 has this JSONB column
    
    # Status and Flags
    status = Column(Enum(PersonStatus, name="person_status"), default=PersonStatus.active, nullable=False)
    is_vip = Column(Boolean, default=False)
    is_watchlist = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)
    
    # Metrics (for recognition performance)
    face_count = Column(Integer, default=0)
    embedding_count = Column(Integer, default=0)
    recognition_count = Column(Integer, default=0)
    
    # Quality Metrics (V1 uses double precision)
    avg_confidence = Column(Float, nullable=True)
    avg_face_quality = Column(Float, nullable=True)
    best_face_quality = Column(Float, nullable=True)
    
    # Timestamps (V1 uses timestamp with time zone)
    first_seen = Column(TIMESTAMP(timezone=True), nullable=True)
    last_seen = Column(TIMESTAMP(timezone=True), nullable=True)
    last_updated = Column(TIMESTAMP(timezone=True), default=func.now(), nullable=False)  # V1 has this NOT NULL
    created_at = Column(TIMESTAMP(timezone=True), default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships (kept simple to avoid V1 ORM issues)
    # embeddings = relationship("EmbeddingModel", back_populates="person", lazy="select")
    
    def __repr__(self):
        return f"<Person {self.first_name} {self.last_name} ({self.person_id})>"


class EmbeddingModel(Base):
    """
    Embedding model - EXACTLY matches V1 schema for data preservation
    Critical: confidence_score column (NOT extraction_confidence)
    """
    __tablename__ = "embeddings"
    
    # Primary Keys
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    person_id = Column(UUID(as_uuid=True), ForeignKey("persons.id"), nullable=False)
    embedding_id = Column(String(255), unique=True, nullable=False, index=True)
    
    # Vector Data (PostgreSQL ARRAY for 512D buffalo_l embeddings)
    vector_data = Column(PG_ARRAY(DECIMAL), nullable=False)
    dimension = Column(Integer, default=512, nullable=False)
    
    # Quality and Status
    status = Column(String(50), default="active", nullable=False)
    quality_score = Column(DECIMAL(5, 3), nullable=True)
    confidence_score = Column(DECIMAL(5, 3), nullable=False)  # CRITICAL: NOT extraction_confidence
    
    # Model Information
    model_name = Column(String(100), default="buffalo_l", nullable=False)
    model_version = Column(String(50), default="1.0.0")
    normalization_method = Column(String(50), default="l2")
    
    # Embedding Flags
    is_primary = Column(Boolean, default=False)
    is_template = Column(Boolean, default=False) 
    is_verified = Column(Boolean, default=False)
    
    # Timestamps
    extracted_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships (kept simple to avoid V1 ORM issues)
    # person = relationship("PersonModel", back_populates="embeddings")
    
    def __repr__(self):
        return f"<Embedding {self.embedding_id} for person {self.person_id}>"


class RecognitionEventModel(Base):
    """
    Recognition event model for analytics and audit trail
    Rule 2: Zero Placeholder Code - Real event tracking
    """
    __tablename__ = "recognition_events"
    
    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_id = Column(String(255), unique=True, nullable=False, index=True)
    
    # Recognition Details
    person_id = Column(UUID(as_uuid=True), ForeignKey("persons.id"), nullable=True)
    embedding_id = Column(UUID(as_uuid=True), ForeignKey("embeddings.id"), nullable=True)
    
    # Recognition Results
    confidence_score = Column(DECIMAL(5, 3), nullable=False)
    recognition_status = Column(String(50), nullable=False)  # recognized, unknown, low_confidence
    
    # Source Information
    camera_id = Column(String(255), nullable=True)
    location = Column(String(255), nullable=True)
    
    # Processing Metadata
    processing_time_ms = Column(Integer, nullable=True)
    model_used = Column(String(100), default="buffalo_l")
    
    # Timestamps
    detected_at = Column(DateTime, nullable=False)
    processed_at = Column(DateTime, default=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<RecognitionEvent {self.event_id} - {self.recognition_status}>"


# Notification System Models (matching existing database schema)

class NotificationChannelModel(Base):
    """
    Notification channel configuration model - matches existing database schema
    Rule 2: Zero Placeholder Code - Real notification channels
    """
    __tablename__ = "notification_channels"
    
    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Channel Information
    channel_name = Column(String(100), unique=True, nullable=False)
    channel_type = Column(String(20), nullable=False)  # VARCHAR with check constraint
    
    # Configuration (channel-specific settings as JSONB)
    configuration = Column(JSONB, nullable=False)
    
    # Status and Limits
    is_active = Column(Boolean, default=True)
    rate_limit_per_minute = Column(Integer, default=60)
    retry_attempts = Column(Integer, default=3)
    timeout_seconds = Column(Integer, default=30)
    
    # Timestamps
    created_at = Column(TIMESTAMP(timezone=True), default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), default=func.now())
    
    def __repr__(self):
        return f"<NotificationChannel {self.channel_name} ({self.channel_type})>"


class AlertRuleModel(Base):
    """
    Alert rule configuration model - matches existing database schema
    Rule 2: Zero Placeholder Code - Real alert rules with trigger conditions
    """
    __tablename__ = "alert_rules"
    
    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Rule Information
    rule_name = Column(String(200), nullable=False)
    description = Column(String, nullable=True)  # TEXT in database
    
    # Trigger Conditions (as JSONB for flexibility)
    trigger_conditions = Column(JSONB, nullable=False)
    
    # Alert Configuration
    priority = Column(String(20), default="medium")  # VARCHAR with check constraint
    cooldown_minutes = Column(Integer, default=30)
    escalation_minutes = Column(Integer, nullable=True)
    auto_resolve_minutes = Column(Integer, nullable=True)
    
    # Notification Settings
    notification_channels = Column(PG_ARRAY(UUID), nullable=False)  # Array of channel IDs
    notification_template = Column(JSONB, nullable=True)  # JSONB, not message_template
    
    # Status and Flags
    is_active = Column(Boolean, default=True)
    created_by = Column(String(100), nullable=True)
    
    # Timestamps
    created_at = Column(TIMESTAMP(timezone=True), default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), default=func.now())
    
    def __repr__(self):
        return f"<AlertRule {self.rule_name} ({self.priority})>"


class AlertInstanceModel(Base):
    """
    Alert instance model - actual triggered alerts
    Rule 2: Zero Placeholder Code - Real alert instances with sighting data
    """
    __tablename__ = "alert_instances"
    
    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Related Entities
    rule_id = Column(UUID(as_uuid=True), ForeignKey("alert_rules.id"), nullable=False)
    person_id = Column(UUID(as_uuid=True), ForeignKey("persons.id"), nullable=True)
    camera_id = Column(String(255), nullable=True)
    sighting_id = Column(String(255), nullable=True)  # Reference to person_sightings
    
    # Alert Data
    confidence_score = Column(DECIMAL(5, 3), nullable=True)
    priority = Column(String(20), nullable=False)  # VARCHAR with check constraint
    status = Column(String(20), default="pending")  # VARCHAR with check constraint
    
    # Alert Content
    alert_message = Column(String(2000), nullable=True)
    alert_metadata = Column(JSONB, nullable=True)  # Additional alert context
    
    # Timestamps
    triggered_at = Column(TIMESTAMP(timezone=True), nullable=False)
    acknowledged_at = Column(TIMESTAMP(timezone=True), nullable=True)
    resolved_at = Column(TIMESTAMP(timezone=True), nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), default=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<AlertInstance {self.id} - {self.status}>"


class NotificationLogModel(Base):
    """
    Notification delivery log model - matches existing database schema
    Rule 2: Zero Placeholder Code - Real notification delivery tracking
    """
    __tablename__ = "notification_logs"
    
    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Related Entities (alert_id is NOT NULL in database)
    alert_id = Column(UUID(as_uuid=True), ForeignKey("alert_instances.id"), nullable=False)
    channel_id = Column(UUID(as_uuid=True), ForeignKey("notification_channels.id"), nullable=False)
    
    # Delivery Information (matching actual database schema)
    delivery_status = Column(String(20), default="pending")  # VARCHAR with check constraint
    sent_at = Column(TIMESTAMP(timezone=True), nullable=True)
    delivered_at = Column(TIMESTAMP(timezone=True), nullable=True)
    error_message = Column(String, nullable=True)  # TEXT in database
    error_code = Column(String(50), nullable=True)
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    next_retry_at = Column(TIMESTAMP(timezone=True), nullable=True)
    external_id = Column(String(255), nullable=True)  # Not delivery_id
    delivery_metadata = Column(JSONB, nullable=True)  # Not delivery_options
    
    # Timestamps
    created_at = Column(TIMESTAMP(timezone=True), default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), default=func.now())
    
    def __repr__(self):
        return f"<NotificationLog {self.id} - {self.delivery_status}>"


class HighPriorityPersonModel(Base):
    """
    High Priority Persons - persons who trigger escalated alerts
    When these persons are detected, alerts go to ALL channels (SMS + Email + Dashboard)
    Rule 1: Incremental Completeness - Simple model for managing high-alert persons
    Rule 2: Zero Placeholder Code - Real database model for alert escalation
    """
    __tablename__ = "high_priority_persons"
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    person_id = Column(UUID(as_uuid=True), ForeignKey("persons.id"), nullable=False, unique=True)
    
    # Alert configuration
    priority_level = Column(String(20), nullable=False, default="high")  # high, critical, wanted
    alert_reason = Column(String, nullable=True)  # Why this person is high priority
    
    # Management metadata
    added_by = Column(String(100), nullable=False)  # Who added them to high priority list
    added_at = Column(TIMESTAMP(timezone=True), default=func.now(), nullable=False)
    last_updated = Column(TIMESTAMP(timezone=True), default=func.now(), onupdate=func.now())
    
    # Status management
    is_active = Column(Boolean, default=True, nullable=False)
    removed_at = Column(TIMESTAMP(timezone=True), nullable=True)
    removed_by = Column(String(100), nullable=True)
    removal_reason = Column(String, nullable=True)
    
    # Alert escalation settings
    escalation_channels = Column(String(200), default="sms,email,dashboard", nullable=False)  # Comma-separated
    notification_frequency = Column(String(20), default="immediate", nullable=False)  # immediate, daily, weekly
    
    def __repr__(self):
        return f"<HighPriorityPerson {self.person_id} - {self.priority_level}>"


class NotificationContactModel(Base):
    """
    Notification Contact Model - manages phone numbers and emails for alert delivery
    Rule 1: Incremental Completeness - Complete contact management system
    Rule 2: Zero Placeholder Code - Real contact storage with verification
    """
    __tablename__ = "notification_contacts"
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    contact_name = Column(String(100), nullable=False)
    contact_type = Column(String(20), nullable=False)  # email, phone, webhook
    contact_value = Column(String(255), nullable=False, unique=True)
    
    # Verification status
    is_primary = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)
    verification_code = Column(String(20), nullable=True)
    verified_at = Column(TIMESTAMP(timezone=True), nullable=True)
    
    # Link to person (optional - for person-specific notifications)
    person_id = Column(UUID(as_uuid=True), ForeignKey("persons.id"), nullable=True)
    
    # Contact metadata
    description = Column(String, nullable=True)
    tags = Column(String(200), nullable=True)
    priority = Column(String(20), default="medium")  # low, medium, high, critical
    
    # Notification preferences
    notification_hours = Column(String(100), nullable=True)  # e.g., '09:00-17:00'
    notification_days = Column(String(50), nullable=True)  # e.g., 'mon,tue,wed,thu,fri'
    max_notifications_per_hour = Column(Integer, default=10)
    
    # Status tracking
    is_active = Column(Boolean, default=True)
    last_notification_sent = Column(TIMESTAMP(timezone=True), nullable=True)
    total_notifications_sent = Column(Integer, default=0)
    failed_attempts = Column(Integer, default=0)
    
    # Audit fields
    added_by = Column(String(100), nullable=False)
    added_at = Column(TIMESTAMP(timezone=True), default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<NotificationContact {self.contact_name} ({self.contact_type}: {self.contact_value})>"