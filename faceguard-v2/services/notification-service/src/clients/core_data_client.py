"""
FACEGUARD V2 NOTIFICATION SERVICE - CORE DATA SERVICE CLIENT
CRITICAL: API-only communication - NO direct database access
Rule 2: Zero Placeholder Code - Real HTTP client implementation
Rule 3: Error-First Development - Comprehensive error handling
"""

import aiohttp
import structlog
from typing import Dict, Any, List, Optional
import asyncio
from datetime import datetime
import json

from config.settings import get_settings

logger = structlog.get_logger(__name__)
settings = get_settings()


class CoreDataServiceError(Exception):
    """Base exception for Core Data Service communication errors"""
    def __init__(self, message: str, status_code: Optional[int] = None, details: Optional[Dict] = None):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class CoreDataServiceClient:
    """
    HTTP Client for Core Data Service Communication
    CRITICAL: Replaces direct database access with API calls
    """
    
    def __init__(self):
        self._session: Optional[aiohttp.ClientSession] = None
        self._base_url = settings.core_data_service_url
        self._timeout = aiohttp.ClientTimeout(total=settings.core_data_timeout_seconds)
        
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session with proper configuration"""
        if self._session is None or self._session.closed:
            connector = aiohttp.TCPConnector(
                limit=settings.http_max_connections,
                limit_per_host=settings.http_connection_pool_size,
                keepalive_timeout=settings.http_keepalive_timeout
            )
            
            self._session = aiohttp.ClientSession(
                connector=connector,
                timeout=self._timeout,
                headers={
                    "Content-Type": "application/json",
                    "User-Agent": f"FaceGuard-NotificationService/{settings.service_version}"
                }
            )
        
        return self._session
    
    async def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request with retry logic and error handling"""
        url = f"{self._base_url}{endpoint}"
        
        for attempt in range(settings.core_data_max_retries + 1):
            try:
                session = await self._get_session()
                async with session.request(method, url, **kwargs) as response:
                    response_text = await response.text()
                    
                    # Log request details
                    await logger.ainfo(
                        "Core Data Service request",
                        method=method,
                        url=url,
                        status=response.status,
                        attempt=attempt + 1
                    )
                    
                    if response.status == 200:
                        return json.loads(response_text)
                    elif response.status == 201:
                        return json.loads(response_text)
                    elif response.status == 204:
                        return {"success": True}
                    elif response.status == 404:
                        raise CoreDataServiceError(
                            f"Resource not found: {endpoint}",
                            status_code=404,
                            details={"url": url}
                        )
                    elif response.status >= 400:
                        try:
                            error_data = json.loads(response_text)
                        except:
                            error_data = {"message": response_text}
                        
                        raise CoreDataServiceError(
                            f"Core Data Service error: {error_data.get('message', 'Unknown error')}",
                            status_code=response.status,
                            details=error_data
                        )
                    
            except CoreDataServiceError:
                raise
            except asyncio.TimeoutError:
                await logger.awarn(
                    "Core Data Service timeout",
                    method=method,
                    url=url,
                    attempt=attempt + 1
                )
                if attempt < settings.core_data_max_retries:
                    await asyncio.sleep(settings.core_data_retry_delay_seconds * (attempt + 1))
                    continue
                raise CoreDataServiceError(
                    f"Core Data Service timeout after {settings.core_data_max_retries} retries",
                    details={"url": url}
                )
            except Exception as e:
                await logger.aerror(
                    "Core Data Service request failed", 
                    method=method,
                    url=url,
                    error=str(e),
                    attempt=attempt + 1
                )
                if attempt < settings.core_data_max_retries:
                    await asyncio.sleep(settings.core_data_retry_delay_seconds * (attempt + 1))
                    continue
                raise CoreDataServiceError(
                    f"Core Data Service communication failed: {str(e)}",
                    details={"url": url, "original_error": str(e)}
                )
        
        raise CoreDataServiceError(
            f"Core Data Service failed after {settings.core_data_max_retries} retries",
            details={"url": url}
        )
    
    # =============================================================================
    # NOTIFICATION CHANNELS API
    # =============================================================================
    
    async def get_notification_channels(self) -> List[Dict[str, Any]]:
        """Get all notification channels from Core Data Service"""
        return await self._make_request("GET", "/notifications/channels")
    
    async def get_notification_channel(self, channel_id: str) -> Dict[str, Any]:
        """Get specific notification channel by ID"""
        return await self._make_request("GET", f"/notifications/channels/{channel_id}")
    
    async def create_notification_channel(self, channel_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new notification channel"""
        return await self._make_request(
            "POST", 
            "/notifications/channels",
            json=channel_data
        )
    
    async def update_notification_channel(self, channel_id: str, channel_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update existing notification channel"""
        return await self._make_request(
            "PUT",
            f"/notifications/channels/{channel_id}",
            json=channel_data
        )
    
    async def delete_notification_channel(self, channel_id: str) -> Dict[str, Any]:
        """Delete notification channel"""
        return await self._make_request("DELETE", f"/notifications/channels/{channel_id}")
    
    async def test_notification_channel(self, channel_id: str) -> Dict[str, Any]:
        """Test notification channel delivery"""
        return await self._make_request("POST", f"/notifications/test-channel/{channel_id}")
    
    # =============================================================================
    # ALERT RULES API
    # =============================================================================
    
    async def get_alert_rules(self) -> List[Dict[str, Any]]:
        """Get all alert rules from Core Data Service"""
        return await self._make_request("GET", "/notifications/alert-rules")
    
    async def get_alert_rule(self, rule_id: str) -> Dict[str, Any]:
        """Get specific alert rule by ID"""
        return await self._make_request("GET", f"/notifications/alert-rules/{rule_id}")
    
    async def create_alert_rule(self, rule_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new alert rule"""
        return await self._make_request(
            "POST",
            "/notifications/alert-rules",
            json=rule_data
        )
    
    async def update_alert_rule(self, rule_id: str, rule_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update existing alert rule"""
        return await self._make_request(
            "PUT",
            f"/notifications/alert-rules/{rule_id}",
            json=rule_data
        )
    
    async def delete_alert_rule(self, rule_id: str) -> Dict[str, Any]:
        """Delete alert rule"""
        return await self._make_request("DELETE", f"/notifications/alert-rules/{rule_id}")
    
    # =============================================================================
    # NOTIFICATION LOGS API
    # =============================================================================
    
    async def get_notification_logs(self, page: int = 1, limit: int = 50, **filters) -> Dict[str, Any]:
        """Get notification logs with pagination and filtering"""
        params = {"page": page, "limit": limit}
        params.update(filters)
        
        return await self._make_request(
            "GET",
            "/notifications/logs",
            params=params
        )
    
    # =============================================================================
    # ALERT HISTORY API  
    # =============================================================================
    
    async def get_alert_history(self, page: int = 1, limit: int = 50, **filters) -> Dict[str, Any]:
        """Get alert history with pagination and filtering"""
        params = {"page": page, "limit": limit}
        params.update(filters)
        
        return await self._make_request(
            "GET", 
            "/notifications/alerts/history",
            params=params
        )
    
    async def acknowledge_alert(self, alert_id: str) -> Dict[str, Any]:
        """Acknowledge alert by ID"""
        return await self._make_request(
            "POST",
            f"/notifications/alerts/{alert_id}/acknowledge"
        )
    
    # =============================================================================
    # ANALYTICS API
    # =============================================================================
    
    async def get_notification_analytics(self) -> Dict[str, Any]:
        """Get notification system analytics"""
        return await self._make_request("GET", "/notifications/analytics")
    
    # =============================================================================
    # HEALTH AND STATUS
    # =============================================================================
    
    async def health_check(self) -> Dict[str, Any]:
        """Check Core Data Service health"""
        try:
            response = await self._make_request("GET", "/health/")
            return {
                "status": "healthy",
                "core_data_service": response,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                "status": "unhealthy", 
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def close(self):
        """Close HTTP session"""
        if self._session and not self._session.closed:
            await self._session.close()


# Global client instance
_core_data_client: Optional[CoreDataServiceClient] = None


async def get_core_data_client() -> CoreDataServiceClient:
    """Get global Core Data Service client instance (singleton pattern)"""
    global _core_data_client
    if _core_data_client is None:
        _core_data_client = CoreDataServiceClient()
    return _core_data_client


async def close_core_data_client():
    """Close global Core Data Service client"""
    global _core_data_client
    if _core_data_client:
        await _core_data_client.close()
        _core_data_client = None