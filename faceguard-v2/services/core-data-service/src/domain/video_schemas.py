"""
FACEGUARD V2 CORE DATA SERVICE - VIDEO PROCESSING SCHEMAS
Rule 2: Zero Placeholder Code - Real Pydantic models for video processing
Rule 3: Error-First Development - Comprehensive validation schemas
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import UUID
import json


class VideoProcessingJobCreate(BaseModel):
    """Schema for creating video processing job"""
    filename: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=500)
    extract_faces: bool = Field(default=True)
    process_immediately: bool = Field(default=True)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    @validator('filename')
    def validate_filename(cls, v):
        if not v or v.isspace():
            raise ValueError('Filename cannot be empty or whitespace')
        return v.strip()
    
    @validator('metadata')
    def validate_metadata(cls, v):
        try:
            # Ensure metadata is JSON serializable
            json.dumps(v)
            return v
        except (TypeError, ValueError):
            raise ValueError('Metadata must be JSON serializable')


class VideoProcessingJobResponse(BaseModel):
    """Schema for video processing job response"""
    job_id: str
    filename: str
    status: str
    progress_percentage: float
    frames_extracted: int
    faces_detected: int
    file_size_bytes: int
    description: Optional[str]
    extract_faces: bool
    processing_time_seconds: float
    error_message: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class VideoFrameCreate(BaseModel):
    """Schema for creating video frame record"""
    frame_id: str
    job_id: str
    timestamp_seconds: float = Field(..., ge=0.0)
    frame_path: str = Field(..., min_length=1)
    face_count: int = Field(default=0, ge=0)
    faces_data: List[Dict[str, Any]] = Field(default_factory=list)
    
    @validator('faces_data')
    def validate_faces_data(cls, v):
        try:
            # Ensure faces data is JSON serializable
            json.dumps(v)
            return v
        except (TypeError, ValueError):
            raise ValueError('Faces data must be JSON serializable')


class VideoFrameResponse(BaseModel):
    """Schema for video frame response"""
    frame_id: str
    job_id: str
    timestamp_seconds: float
    frame_path: str
    face_count: int
    faces_data: List[Dict[str, Any]]
    created_at: datetime
    
    class Config:
        from_attributes = True


class VideoProcessingRequest(BaseModel):
    """Schema for video processing request parameters"""
    extract_faces: bool = Field(default=True)
    face_detection_threshold: float = Field(default=0.7, ge=0.0, le=1.0)
    frame_extraction_interval: float = Field(default=1.0, gt=0.0, le=10.0)
    max_frames: Optional[int] = Field(None, gt=0, le=10000)
    save_frames: bool = Field(default=True)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class VideoProcessingStats(BaseModel):
    """Schema for video processing statistics"""
    total_jobs: int
    pending_jobs: int
    processing_jobs: int
    completed_jobs: int
    failed_jobs: int
    total_frames_extracted: int
    total_faces_detected: int
    average_processing_time_seconds: float
    total_storage_mb: float


class VideoUploadValidation(BaseModel):
    """Schema for video upload validation result"""
    valid: bool
    file_size_mb: float
    duration_seconds: Optional[float]
    fps: Optional[float]
    resolution: Optional[str]
    format: str
    error_message: Optional[str]
    warnings: List[str] = Field(default_factory=list)


class VideoBatchProcessingRequest(BaseModel):
    """Schema for batch video processing request"""
    job_ids: List[str] = Field(..., min_items=1, max_items=100)
    processing_options: VideoProcessingRequest
    priority: str = Field(default="normal", pattern="^(low|normal|high|urgent)$")
    notification_email: Optional[str] = Field(None, pattern=r'^[^@]+@[^@]+\.[^@]+$')
    
    @validator('job_ids')
    def validate_job_ids(cls, v):
        # Validate each job_id is a valid UUID
        for job_id in v:
            try:
                UUID(job_id)
            except ValueError:
                raise ValueError(f'Invalid job ID format: {job_id}')
        return v