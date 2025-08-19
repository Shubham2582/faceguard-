"""
Database Models for Face Recognition Service
Must match V1 schema EXACTLY for data preservation
Critical: Use confidence_score (NOT extraction_confidence)
"""

from sqlalchemy import Column, String, Integer, DateTime, Boolean, DECIMAL, ForeignKey, ARRAY, Enum, Float
from sqlalchemy.dialects.postgresql import UUID, ARRAY as PG_ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import uuid
import enum

from storage.database import Base


# V1 Database ENUM Types (must match exactly)
class PersonStatus(enum.Enum):
    active = "active"
    inactive = "inactive"
    blocked = "blocked"
    pending = "pending"
    archived = "archived"


class AccessLevel(enum.Enum):
    visitor = "visitor"
    employee = "employee"
    contractor = "contractor"
    admin = "admin"
    security = "security"
    vip = "vip"


class PersonModel(Base):
    """
    Person model - Read-only access for recognition service
    Matches V1 schema exactly
    """
    __tablename__ = "persons"
    
    # Primary Keys
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    person_id = Column(String(100), unique=True, nullable=False)
    
    # Personal Information
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    
    # Status and Access
    status = Column(Enum(PersonStatus, name="person_status"), default=PersonStatus.active)
    access_level = Column(Enum(AccessLevel, name="accesslevel"), default=AccessLevel.visitor)
    
    # Metrics (these will be updated after recognition)
    embedding_count = Column(Integer, default=0, nullable=False)
    recognition_count = Column(Integer, default=0, nullable=False)
    avg_confidence = Column(Float, nullable=True)
    last_seen = Column(DateTime(timezone=True), nullable=True)
    
    # Flags
    is_vip = Column(Boolean, default=False, nullable=False)
    is_watchlist = Column(Boolean, default=False, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class EmbeddingModel(Base):
    """
    Embedding model for face recognition vectors
    Critical: confidence_score field (NOT extraction_confidence)
    """
    __tablename__ = "embeddings"
    
    # Primary Keys
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    embedding_id = Column(String(255), unique=True, nullable=False)
    
    # Foreign Key
    person_id = Column(UUID(as_uuid=True), ForeignKey("persons.id"), nullable=False)
    
    # Vector Data - PostgreSQL ARRAY of DECIMAL
    vector_data = Column(ARRAY(DECIMAL), nullable=False)  # 512-dimensional vector
    dimension = Column(Integer, default=512, nullable=False)
    
    # Quality Metrics
    confidence_score = Column(Float, nullable=True)  # CRITICAL: V1 column name
    quality_score = Column(Float, nullable=True)
    vector_norm = Column(Float, nullable=True)
    
    # Model Information
    model_name = Column(String(100), default="buffalo_l", nullable=False)
    model_version = Column(String(50), default="1.0.0", nullable=False)
    
    # Status
    status = Column(String(50), default="active", nullable=False)
    is_primary = Column(Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    extraction_timestamp = Column(DateTime(timezone=True), nullable=True)


class RecognitionEventModel(Base):
    """
    Recognition event logging for audit trail
    Real events, no mock data
    """
    __tablename__ = "recognition_events"
    
    # Primary Keys
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_id = Column(String(255), unique=True, nullable=False)
    
    # Foreign Keys
    person_id = Column(UUID(as_uuid=True), ForeignKey("persons.id"), nullable=True)
    embedding_id = Column(UUID(as_uuid=True), ForeignKey("embeddings.id"), nullable=True)
    
    # Recognition Details
    confidence_score = Column(Float, nullable=False)
    similarity_score = Column(Float, nullable=False)
    face_quality = Column(Float, nullable=True)
    
    # Processing Information
    processing_time_ms = Column(Integer, nullable=False)
    gpu_used = Column(Boolean, default=False, nullable=False)
    model_name = Column(String(100), default="buffalo_l", nullable=False)
    
    # Image Information
    image_width = Column(Integer, nullable=True)
    image_height = Column(Integer, nullable=True)
    face_count = Column(Integer, default=1, nullable=False)
    
    # Location/Camera Information
    camera_id = Column(String(100), nullable=True)
    location = Column(String(255), nullable=True)
    
    # Timestamps
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)