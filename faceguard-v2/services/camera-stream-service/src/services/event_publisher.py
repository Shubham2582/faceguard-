"""
Event Publishing Service for Face Recognition Events
Following FACEGUARD_V2_STRATEGIC_IMPLEMENTATION_GUIDE.md - Phase 4 Event System
Real Redis pub/sub implementation - Zero Placeholder Code
"""
import asyncio
import json
import logging
import redis.asyncio as redis
from datetime import datetime
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, asdict

from ..config.settings import Settings
from ..domain.models import FrameMetadata

logger = logging.getLogger(__name__)


@dataclass
class RecognitionEvent:
    """Recognition event schema for pub/sub"""
    event_id: str
    timestamp: datetime
    camera_id: str
    frame_id: str
    persons_detected: List[Dict[str, Any]]
    processing_time_ms: float
    confidence_threshold: float
    frame_metadata: Dict[str, Any]
    recognition_successful: bool
    event_type: str = "face_recognition"
    service_version: str = "2.0.0"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data


class EventPublisher:
    """
    Redis-based event publisher for real-time recognition events
    Real implementation with connection pooling and error handling
    """
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.redis_pool: Optional[redis.ConnectionPool] = None
        self.redis_client: Optional[redis.Redis] = None
        
        # Event configuration
        self.event_channel = settings.event_channel
        self.enable_persistence = settings.enable_event_persistence
        self.batch_size = settings.event_batch_size
        
        # Performance tracking
        self.events_published = 0
        self.events_failed = 0
        self.last_publish_time: Optional[datetime] = None
        self.last_error: Optional[str] = None
        
        # Event batching for persistence
        self.event_batch: List[RecognitionEvent] = []
        self.batch_lock = asyncio.Lock()
        
    async def initialize(self):
        """Initialize Redis connection pool"""
        logger.info("Initializing Event Publisher with Redis")
        
        try:
            # Create Redis connection pool
            self.redis_pool = redis.ConnectionPool(
                host=self.settings.redis_host,
                port=self.settings.redis_port,
                db=self.settings.redis_db,
                decode_responses=True,
                max_connections=10
            )
            
            self.redis_client = redis.Redis(connection_pool=self.redis_pool)
            
            # Test connection
            await self._test_redis_connectivity()
            
            logger.info(f"Event Publisher initialized successfully - Channel: {self.event_channel}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Event Publisher: {str(e)}")
            self.last_error = f"Initialization failed: {str(e)}"
            raise
            
    async def shutdown(self):
        """Shutdown publisher and flush pending events"""
        logger.info("Shutting down Event Publisher")
        
        try:
            # Flush any pending batched events
            if self.event_batch:
                await self._flush_event_batch()
            
            # Close Redis connections
            if self.redis_client:
                await self.redis_client.aclose()
            
            if self.redis_pool:
                await self.redis_pool.aclose()
                
            logger.info("Event Publisher shutdown complete")
            
        except Exception as e:
            logger.error(f"Error during Event Publisher shutdown: {str(e)}")
    
    async def _test_redis_connectivity(self):
        """Test Redis connection"""
        try:
            if not self.redis_client:
                raise Exception("Redis client not initialized")
                
            await self.redis_client.ping()
            logger.info("Redis connectivity confirmed")
            return True
            
        except Exception as e:
            logger.error(f"Redis connectivity test failed: {str(e)}")
            self.last_error = f"Redis connectivity failed: {str(e)}"
            return False
    
    async def publish_recognition_event(
        self,
        camera_id: str,
        frame_id: str,
        persons_detected: List[Dict[str, Any]],
        processing_time_ms: float,
        confidence_threshold: float,
        frame_metadata: FrameMetadata,
        recognition_successful: bool
    ) -> bool:
        """
        Publish recognition event to Redis pub/sub channel
        Real-time event publishing with error handling
        """
        try:
            if not self.redis_client:
                logger.warning("Event Publisher not initialized, skipping event")
                return False
            
            # Create recognition event
            import uuid
            event = RecognitionEvent(
                event_id=str(uuid.uuid4()),
                timestamp=datetime.utcnow(),
                camera_id=camera_id,
                frame_id=frame_id,
                persons_detected=persons_detected,
                processing_time_ms=processing_time_ms,
                confidence_threshold=confidence_threshold,
                frame_metadata={
                    "width": frame_metadata.width,
                    "height": frame_metadata.height,
                    "quality_score": frame_metadata.quality_score,
                    "frame_number": frame_metadata.frame_number,
                    "file_size": frame_metadata.file_size
                },
                recognition_successful=recognition_successful
            )
            
            # Publish event to Redis channel
            event_json = json.dumps(event.to_dict())
            
            # Real-time publish
            published = await self.redis_client.publish(self.event_channel, event_json)
            
            if published > 0:
                self.events_published += 1
                self.last_publish_time = datetime.utcnow()
                
                logger.debug(f"Recognition event published: {event.event_id} "
                           f"(subscribers: {published}, camera: {camera_id})")
                
                # Add to batch for persistence if enabled
                if self.enable_persistence:
                    await self._add_to_batch(event)
                
                return True
            else:
                logger.warning(f"Event published but no subscribers listening on {self.event_channel}")
                return True  # Still successful publish, just no subscribers
                
        except Exception as e:
            self.events_failed += 1
            self.last_error = f"Event publish failed: {str(e)}"
            logger.error(f"Failed to publish recognition event: {str(e)}")
            return False
    
    async def _add_to_batch(self, event: RecognitionEvent):
        """Add event to batch for persistence"""
        async with self.batch_lock:
            self.event_batch.append(event)
            
            # Flush batch if it reaches the batch size
            if len(self.event_batch) >= self.batch_size:
                await self._flush_event_batch()
    
    async def _flush_event_batch(self):
        """Flush event batch to Redis for persistence"""
        if not self.event_batch or not self.redis_client:
            return
            
        try:
            # Store events in Redis list for persistence
            events_json = [json.dumps(event.to_dict()) for event in self.event_batch]
            
            # Use Redis LPUSH to add events to persistent list
            persistence_key = f"{self.event_channel}:history"
            await self.redis_client.lpush(persistence_key, *events_json)
            
            # Optional: Set TTL for event history (e.g., 7 days)
            await self.redis_client.expire(persistence_key, 604800)  # 7 days
            
            logger.debug(f"Flushed {len(self.event_batch)} events to persistence storage")
            self.event_batch.clear()
            
        except Exception as e:
            logger.error(f"Failed to flush event batch: {str(e)}")
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get event publishing performance statistics"""
        return {
            "events_published": self.events_published,
            "events_failed": self.events_failed,
            "success_rate_percent": (
                (self.events_published / max(self.events_published + self.events_failed, 1)) * 100
            ),
            "last_publish_time": self.last_publish_time.isoformat() if self.last_publish_time else None,
            "last_error": self.last_error,
            "event_channel": self.event_channel,
            "persistence_enabled": self.enable_persistence,
            "pending_batch_size": len(self.event_batch)
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check for event publisher"""
        try:
            connectivity_ok = await self._test_redis_connectivity()
            stats = self.get_performance_stats()
            
            # Determine health status
            if not connectivity_ok:
                status = "unhealthy"
            elif stats["events_failed"] > 0 and stats["success_rate_percent"] < 90:
                status = "degraded"
            else:
                status = "healthy"
            
            return {
                "status": status,
                "redis_connectivity": connectivity_ok,
                "performance": stats,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }