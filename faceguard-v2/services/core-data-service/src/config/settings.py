"""
FACEGUARD V2 CORE DATA SERVICE CONFIGURATION
Rule 2: Zero Placeholder Code - Real configuration management
Rule 3: Error-First Development - Proper validation and error handling
"""

from pydantic_settings import BaseSettings
from pydantic import Field, validator
from typing import Optional
import os
from pathlib import Path


class Settings(BaseSettings):
    """Configuration settings with type safety and validation"""
    
    # Database Configuration (LOCAL PostgreSQL - NEVER Docker)
    database_host: str = Field(default="localhost", description="PostgreSQL host")
    database_port: int = Field(default=5432, description="PostgreSQL port") 
    database_user: str = Field(default="postgres", description="PostgreSQL user")
    database_password: str = Field(default="1234", description="PostgreSQL password")
    database_name: str = Field(default="faceguard", description="PostgreSQL database name")
    
    # Service Configuration
    service_host: str = Field(default="0.0.0.0", description="Service host")
    service_port: int = Field(default=8001, description="Service port")
    service_version: str = Field(default="2.0.0", description="Service version")
    
    # Feature Flags (ALL ENABLED - NO DISABLED FEATURES)
    enable_analytics: bool = Field(default=True, description="Enable analytics")
    enable_faiss: bool = Field(default=True, description="Enable FAISS operations")
    enable_migration: bool = Field(default=True, description="Enable data migration")
    enable_health_checks: bool = Field(default=True, description="Enable health checks")
    
    # FAISS Configuration
    faiss_index_path: str = Field(default="../../data/faiss/index.bin", description="FAISS index path")
    faiss_metadata_path: str = Field(default="../../data/faiss/metadata.json", description="FAISS metadata path")
    vector_dimension: int = Field(default=512, description="Vector dimension")
    
    # Logging Configuration
    log_level: str = Field(default="INFO", description="Logging level")
    log_format: str = Field(default="json", description="Log format")
    
    @validator('database_port')
    def validate_port(cls, v):
        if not (1 <= v <= 65535):
            raise ValueError('Port must be between 1 and 65535')
        return v
    
    @validator('vector_dimension')
    def validate_vector_dimension(cls, v):
        if v != 512:
            raise ValueError('Vector dimension must be 512 for buffalo_l compatibility')
        return v
    
    @validator('database_password')
    def validate_password_not_empty(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Database password cannot be empty')
        return v
    
    @property
    def database_url(self) -> str:
        """Construct database URL for SQLAlchemy"""
        return f"postgresql+asyncpg://{self.database_user}:{self.database_password}@{self.database_host}:{self.database_port}/{self.database_name}"
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode"""
        return self.log_level.upper() in ["WARNING", "ERROR"]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get settings instance for dependency injection"""
    return settings