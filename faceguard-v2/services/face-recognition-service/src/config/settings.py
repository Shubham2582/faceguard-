"""
Face Recognition Service Configuration
Prevention Rules:
- Rule 2: Zero Placeholder Code - All real implementations
- Rule 3: Error-First Development - Proper error handling
"""

from pydantic_settings import BaseSettings
from pydantic import Field, validator
from typing import Optional


class Settings(BaseSettings):
    """
    Face Recognition Service Settings
    Following core-data-service patterns for consistency
    """
    
    # Service Configuration
    service_name: str = Field(default="face-recognition-service", description="Service identifier")
    service_version: str = Field(default="2.0.0", description="Service version")
    service_host: str = Field(default="0.0.0.0", description="Service host")
    service_port: int = Field(default=8002, description="Service port")
    
    # Database Configuration (LOCAL PostgreSQL - NEVER Docker)
    database_host: str = Field(default="localhost", description="PostgreSQL host")
    database_port: int = Field(default=5432, description="PostgreSQL port")
    database_name: str = Field(default="faceguard", description="Database name")
    database_user: str = Field(default="postgres", description="Database user")
    database_password: str = Field(default="1234", description="Database password")
    
    # Recognition Configuration
    recognition_threshold: float = Field(default=0.6, description="60% similarity threshold")
    detection_confidence: float = Field(default=0.5, description="Min face detection confidence")
    gpu_enabled: bool = Field(default=True, description="Use GPU for recognition")
    model_name: str = Field(default="buffalo_l", description="InsightFace model")
    
    # Processing Configuration  
    max_faces_per_image: int = Field(default=10, description="Max faces to process per image")
    embedding_dimension: int = Field(default=512, description="Embedding vector dimension")
    batch_size: int = Field(default=1, description="Processing batch size")
    
    # Feature Flags (ALL ENABLED - No disabled features)
    enable_gpu_acceleration: bool = Field(default=True, description="GPU acceleration")
    enable_metrics_tracking: bool = Field(default=True, description="Real metrics tracking")
    enable_quality_assessment: bool = Field(default=True, description="Image quality checks")
    enable_face_alignment: bool = Field(default=True, description="Face alignment")
    
    # Integration
    core_data_service_url: str = Field(
        default="http://localhost:8001",
        description="Core Data Service URL"
    )
    
    # Logging
    log_level: str = Field(default="INFO", description="Logging level")
    log_format: str = Field(default="json", description="Log format")
    
    @validator('recognition_threshold')
    def validate_threshold(cls, v):
        """Ensure threshold is between 0 and 1"""
        if not 0 < v <= 1:
            raise ValueError("Recognition threshold must be between 0 and 1")
        return v
    
    @validator('database_password')
    def validate_password(cls, v):
        """Never allow empty password for security"""
        if not v:
            raise ValueError("Database password cannot be empty")
        return v
    
    @property
    def database_url(self) -> str:
        """PostgreSQL connection URL"""
        return (
            f"postgresql+asyncpg://{self.database_user}:{self.database_password}"
            f"@{self.database_host}:{self.database_port}/{self.database_name}"
        )
    
    @property
    def sync_database_url(self) -> str:
        """Synchronous PostgreSQL URL for certain operations"""
        return (
            f"postgresql://{self.database_user}:{self.database_password}"
            f"@{self.database_host}:{self.database_port}/{self.database_name}"
        )
    
    class Config:
        env_prefix = "FACE_RECOGNITION_"
        case_sensitive = False
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()