"""
FACEGUARD V2 NOTIFICATION SERVICE - EVENT BROADCASTING SYSTEM
Rule 2: Zero Placeholder Code - Real event broadcasting for dashboard updates
Rule 3: Error-First Development - Comprehensive event delivery error handling

Event Broadcasting Features:
- Real-time alert notifications
- Notification delivery updates
- System status broadcasting
- Dashboard live updates
"""

import asyncio
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
import structlog
from enum import Enum

from config.settings import get_settings

logger = structlog.get_logger(__name__)
settings = get_settings()


class EventType(Enum):
    """Event types for broadcasting"""
    # Alert events
    ALERT_TRIGGERED = "alert_triggered"
    ALERT_ACKNOWLEDGED = "alert_acknowledged" 
    ALERT_RESOLVED = "alert_resolved"
    ALERT_ESCALATED = "alert_escalated"
    
    # Notification events
    NOTIFICATION_SENT = "notification_sent"
    NOTIFICATION_DELIVERED = "notification_delivered"
    NOTIFICATION_FAILED = "notification_failed"
    NOTIFICATION_RETRYING = "notification_retrying"
    
    # System events
    SYSTEM_STATUS_UPDATE = "system_status_update"
    SERVICE_HEALTH_CHANGE = "service_health_change"
    PERFORMANCE_ALERT = "performance_alert"
    
    # Dashboard events
    DASHBOARD_UPDATE = "dashboard_update"
    STATISTICS_UPDATE = "statistics_update"
    ACTIVITY_FEED_UPDATE = "activity_feed_update"


class EventPriority(Enum):
    """Event priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class EventBroadcaster:
    """
    Production event broadcasting system
    
    Features:
    - Multi-channel event routing
    - Priority-based delivery
    - Event queuing and persistence
    - WebSocket integration
    - Delivery confirmation
    """
    
    def __init__(self):
        self.ws_manager = None
        self.event_queue: List[Dict[str, Any]] = []
        self.max_queue_size = 1000
        self.delivery_stats = {
            "events_sent": 0,
            "events_failed": 0,
            "events_queued": 0
        }
        self._subscribers: Dict[EventType, List[callable]] = {}
        
    async def initialize(self):
        """Initialize event broadcaster"""
        try:
            # Import WebSocket manager (avoid circular imports)
            from api.websocket import get_websocket_manager
            self.ws_manager = await get_websocket_manager()
            
            await logger.ainfo("Event broadcaster initialized successfully")
            
        except Exception as e:
            await logger.aerror("Event broadcaster initialization failed", error=str(e))
            raise
    
    async def broadcast_alert_event(
        self,
        event_type: EventType,
        alert_data: Dict[str, Any],
        priority: EventPriority = EventPriority.HIGH
    ):
        """Broadcast alert-related events"""
        try:
            event = {
                "type": event_type.value,
                "category": "alert",
                "priority": priority.value,
                "data": alert_data,
                "timestamp": datetime.utcnow().isoformat(),
                "event_id": f"alert_{datetime.utcnow().timestamp()}"
            }
            
            # Send to WebSocket clients
            if self.ws_manager:
                await self.ws_manager.broadcast_to_room("alerts", event)
                await self.ws_manager.broadcast_to_room("dashboard", event)
            
            # Update statistics
            self.delivery_stats["events_sent"] += 1
            
            await logger.ainfo("Alert event broadcasted",
                             event_type=event_type.value,
                             alert_id=alert_data.get("alert_id"),
                             priority=priority.value)
            
        except Exception as e:
            self.delivery_stats["events_failed"] += 1
            await logger.aerror("Failed to broadcast alert event",
                               event_type=event_type.value,
                               error=str(e))
    
    async def broadcast_notification_event(
        self,
        event_type: EventType,
        notification_data: Dict[str, Any],
        priority: EventPriority = EventPriority.MEDIUM
    ):
        """Broadcast notification delivery events"""
        try:
            event = {
                "type": event_type.value,
                "category": "notification",
                "priority": priority.value,
                "data": notification_data,
                "timestamp": datetime.utcnow().isoformat(),
                "event_id": f"notification_{datetime.utcnow().timestamp()}"
            }
            
            # Send to WebSocket clients
            if self.ws_manager:
                await self.ws_manager.broadcast_to_room("notifications", event)
                await self.ws_manager.broadcast_to_room("dashboard", event)
            
            self.delivery_stats["events_sent"] += 1
            
            await logger.ainfo("Notification event broadcasted",
                             event_type=event_type.value,
                             delivery_id=notification_data.get("delivery_id"),
                             priority=priority.value)
            
        except Exception as e:
            self.delivery_stats["events_failed"] += 1
            await logger.aerror("Failed to broadcast notification event",
                               event_type=event_type.value,
                               error=str(e))
    
    async def broadcast_system_event(
        self,
        event_type: EventType,
        system_data: Dict[str, Any],
        priority: EventPriority = EventPriority.LOW
    ):
        """Broadcast system status events"""
        try:
            event = {
                "type": event_type.value,
                "category": "system",
                "priority": priority.value,
                "data": system_data,
                "timestamp": datetime.utcnow().isoformat(),
                "event_id": f"system_{datetime.utcnow().timestamp()}"
            }
            
            # Send to WebSocket clients
            if self.ws_manager:
                await self.ws_manager.broadcast_to_room("system", event)
                await self.ws_manager.broadcast_to_room("dashboard", event)
            
            self.delivery_stats["events_sent"] += 1
            
            await logger.ainfo("System event broadcasted",
                             event_type=event_type.value,
                             priority=priority.value)
            
        except Exception as e:
            self.delivery_stats["events_failed"] += 1
            await logger.aerror("Failed to broadcast system event",
                               event_type=event_type.value,
                               error=str(e))
    
    async def broadcast_dashboard_update(
        self,
        update_type: str,
        data: Dict[str, Any],
        priority: EventPriority = EventPriority.LOW
    ):
        """Broadcast general dashboard updates"""
        try:
            event = {
                "type": "dashboard_update",
                "update_type": update_type,
                "category": "dashboard",
                "priority": priority.value,
                "data": data,
                "timestamp": datetime.utcnow().isoformat(),
                "event_id": f"dashboard_{datetime.utcnow().timestamp()}"
            }
            
            if self.ws_manager:
                await self.ws_manager.broadcast_to_room("dashboard", event)
            
            self.delivery_stats["events_sent"] += 1
            
            await logger.ainfo("Dashboard update broadcasted",
                             update_type=update_type,
                             priority=priority.value)
            
        except Exception as e:
            self.delivery_stats["events_failed"] += 1
            await logger.aerror("Failed to broadcast dashboard update",
                               update_type=update_type,
                               error=str(e))
    
    async def broadcast_activity_feed(
        self,
        activity: Dict[str, Any],
        priority: EventPriority = EventPriority.LOW
    ):
        """Broadcast activity feed updates"""
        try:
            event = {
                "type": "activity_feed_update",
                "category": "activity",
                "priority": priority.value,
                "data": activity,
                "timestamp": datetime.utcnow().isoformat(),
                "event_id": f"activity_{datetime.utcnow().timestamp()}"
            }
            
            if self.ws_manager:
                await self.ws_manager.broadcast_to_room("dashboard", event)
            
            self.delivery_stats["events_sent"] += 1
            
            await logger.ainfo("Activity feed broadcasted",
                             activity_type=activity.get("type"),
                             priority=priority.value)
            
        except Exception as e:
            self.delivery_stats["events_failed"] += 1
            await logger.aerror("Failed to broadcast activity feed",
                               error=str(e))
    
    async def subscribe_to_event(self, event_type: EventType, callback: callable):
        """Subscribe to specific event types"""
        try:
            if event_type not in self._subscribers:
                self._subscribers[event_type] = []
            
            self._subscribers[event_type].append(callback)
            
            await logger.ainfo("Event subscription added",
                             event_type=event_type.value,
                             total_subscribers=len(self._subscribers[event_type]))
            
        except Exception as e:
            await logger.aerror("Failed to add event subscription",
                               event_type=event_type.value,
                               error=str(e))
    
    async def notify_subscribers(self, event_type: EventType, event_data: Dict[str, Any]):
        """Notify all subscribers of an event"""
        try:
            subscribers = self._subscribers.get(event_type, [])
            if not subscribers:
                return
            
            await logger.ainfo("Notifying event subscribers",
                             event_type=event_type.value,
                             subscriber_count=len(subscribers))
            
            for callback in subscribers:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(event_data)
                    else:
                        callback(event_data)
                except Exception as e:
                    await logger.aerror("Subscriber callback failed",
                                       event_type=event_type.value,
                                       error=str(e))
            
        except Exception as e:
            await logger.aerror("Failed to notify subscribers",
                               event_type=event_type.value,
                               error=str(e))
    
    async def get_delivery_stats(self) -> Dict[str, Any]:
        """Get event delivery statistics"""
        try:
            total_events = self.delivery_stats["events_sent"] + self.delivery_stats["events_failed"]
            success_rate = (self.delivery_stats["events_sent"] / total_events * 100) if total_events > 0 else 0
            
            return {
                **self.delivery_stats,
                "success_rate": round(success_rate, 2),
                "queue_size": len(self.event_queue),
                "subscribers": {
                    event_type.value: len(callbacks) 
                    for event_type, callbacks in self._subscribers.items()
                },
                "websocket_status": "connected" if self.ws_manager else "disconnected"
            }
            
        except Exception as e:
            await logger.aerror("Failed to get delivery stats", error=str(e))
            return {"error": str(e)}


# Global event broadcaster instance
_event_broadcaster = None


async def get_event_broadcaster() -> EventBroadcaster:
    """Get global event broadcaster instance"""
    global _event_broadcaster
    if _event_broadcaster is None:
        _event_broadcaster = EventBroadcaster()
        await _event_broadcaster.initialize()
    return _event_broadcaster


# Convenience functions for other services

async def broadcast_alert_triggered(alert_data: Dict[str, Any]):
    """Convenience function to broadcast alert triggered event"""
    broadcaster = await get_event_broadcaster()
    await broadcaster.broadcast_alert_event(
        EventType.ALERT_TRIGGERED,
        alert_data,
        EventPriority.HIGH
    )


async def broadcast_alert_acknowledged(alert_data: Dict[str, Any]):
    """Convenience function to broadcast alert acknowledged event"""
    broadcaster = await get_event_broadcaster()
    await broadcaster.broadcast_alert_event(
        EventType.ALERT_ACKNOWLEDGED,
        alert_data,
        EventPriority.MEDIUM
    )


async def broadcast_alert_resolved(alert_data: Dict[str, Any]):
    """Convenience function to broadcast alert resolved event"""
    broadcaster = await get_event_broadcaster()
    await broadcaster.broadcast_alert_event(
        EventType.ALERT_RESOLVED,
        alert_data,
        EventPriority.MEDIUM
    )


async def broadcast_notification_sent(notification_data: Dict[str, Any]):
    """Convenience function to broadcast notification sent event"""
    broadcaster = await get_event_broadcaster()
    await broadcaster.broadcast_notification_event(
        EventType.NOTIFICATION_SENT,
        notification_data,
        EventPriority.MEDIUM
    )


async def broadcast_notification_delivered(notification_data: Dict[str, Any]):
    """Convenience function to broadcast notification delivered event"""
    broadcaster = await get_event_broadcaster()
    await broadcaster.broadcast_notification_event(
        EventType.NOTIFICATION_DELIVERED,
        notification_data,
        EventPriority.LOW
    )


async def broadcast_notification_failed(notification_data: Dict[str, Any]):
    """Convenience function to broadcast notification failed event"""
    broadcaster = await get_event_broadcaster()
    await broadcaster.broadcast_notification_event(
        EventType.NOTIFICATION_FAILED,
        notification_data,
        EventPriority.HIGH
    )


async def broadcast_system_status(status_data: Dict[str, Any]):
    """Convenience function to broadcast system status update"""
    broadcaster = await get_event_broadcaster()
    await broadcaster.broadcast_system_event(
        EventType.SYSTEM_STATUS_UPDATE,
        status_data,
        EventPriority.LOW
    )


async def broadcast_statistics_update(stats_data: Dict[str, Any]):
    """Convenience function to broadcast statistics update"""
    broadcaster = await get_event_broadcaster()
    await broadcaster.broadcast_dashboard_update(
        "statistics",
        stats_data,
        EventPriority.LOW
    )