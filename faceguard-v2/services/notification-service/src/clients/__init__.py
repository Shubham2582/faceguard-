"""
FACEGUARD V2 NOTIFICATION SERVICE - CLIENT MODULES
HTTP clients for inter-service communication
"""

from .core_data_client import (
    CoreDataServiceClient,
    CoreDataServiceError,
    get_core_data_client,
    close_core_data_client
)

__all__ = [
    "CoreDataServiceClient",
    "CoreDataServiceError", 
    "get_core_data_client",
    "close_core_data_client"
]