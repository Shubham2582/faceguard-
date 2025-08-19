"""
FACEGUARD V2 CORE DATA SERVICE - WEBSOCKET MANAGER
Rule 1: Incremental Completeness - Real-time dashboard notifications
Rule 2: Zero Placeholder Code - Real WebSocket connections and broadcasting
Rule 3: Error-First Development - Comprehensive connection management
"""

from fastapi import WebSocket, WebSocketDisconnect
from typing import List, Dict, Any, Optional
import json
import structlog
from datetime import datetime
import asyncio
from uuid import uuid4

logger = structlog.get_logger(__name__)


class WebSocketConnectionManager:
    """
    Manages WebSocket connections for real-time dashboard notifications
    Handles multiple clients and broadcasts updates efficiently
    """
    
    def __init__(self):
        # Store active connections with metadata
        self.active_connections: Dict[str, Dict[str, Any]] = {}
        self.connection_stats = {
            "total_connections": 0,
            "active_connections": 0,
            "messages_sent": 0,
            "last_activity": None
        }
    
    async def connect(self, websocket: WebSocket, client_info: Optional[Dict[str, Any]] = None) -> str:
        """
        Accept new WebSocket connection and register client
        Returns connection ID for tracking
        """
        await websocket.accept()
        
        # Generate unique connection ID
        connection_id = str(uuid4())
        
        # Store connection with metadata
        self.active_connections[connection_id] = {
            "websocket": websocket,
            "connected_at": datetime.utcnow(),
            "client_info": client_info or {},
            "messages_received": 0,
            "messages_sent": 0,
            "last_activity": datetime.utcnow()
        }
        
        # Update stats
        self.connection_stats["total_connections"] += 1
        self.connection_stats["active_connections"] = len(self.active_connections)
        self.connection_stats["last_activity"] = datetime.utcnow()
        
        await logger.ainfo(
            "WebSocket client connected",
            connection_id=connection_id,
            client_info=client_info,
            active_connections=len(self.active_connections)
        )
        
        # Send welcome message with connection info
        welcome_message = {
            "type": "connection_established",
            "connection_id": connection_id,
            "timestamp": datetime.utcnow().isoformat(),
            "server_info": {
                "service": "faceguard-v2-core-data",
                "version": "2.0.0",
                "websocket_features": [
                    "real_time_alerts",
                    "person_sightings",
                    "system_status",
                    "camera_updates"
                ]
            }
        }
        
        await self._send_to_connection(connection_id, welcome_message)
        
        return connection_id
    
    async def disconnect(self, connection_id: str):
        """
        Disconnect and clean up WebSocket connection
        """
        if connection_id in self.active_connections:
            connection_info = self.active_connections[connection_id]
            
            # Log connection statistics
            duration = datetime.utcnow() - connection_info["connected_at"]
            
            await logger.ainfo(
                "WebSocket client disconnected",
                connection_id=connection_id,
                duration_seconds=duration.total_seconds(),
                messages_sent=connection_info["messages_sent"],
                messages_received=connection_info["messages_received"]
            )
            
            # Remove from active connections
            del self.active_connections[connection_id]
            
            # Update stats
            self.connection_stats["active_connections"] = len(self.active_connections)
    
    async def _send_to_connection(self, connection_id: str, message: Dict[str, Any]) -> bool:
        """
        Send message to specific connection with error handling
        Returns True if successful, False if connection is broken
        """
        if connection_id not in self.active_connections:
            return False
        
        connection_info = self.active_connections[connection_id]
        websocket = connection_info["websocket"]
        
        try:
            # Add timestamp to all messages
            message["timestamp"] = datetime.utcnow().isoformat()
            
            await websocket.send_text(json.dumps(message))
            
            # Update connection stats
            connection_info["messages_sent"] += 1
            connection_info["last_activity"] = datetime.utcnow()
            self.connection_stats["messages_sent"] += 1
            
            return True
            
        except WebSocketDisconnect:
            await logger.awarn(
                "WebSocket connection lost during send",
                connection_id=connection_id
            )
            await self.disconnect(connection_id)
            return False
        except Exception as e:
            await logger.aerror(
                "Failed to send WebSocket message",
                connection_id=connection_id,
                error=str(e)
            )
            return False
    
    async def broadcast_to_all(self, message: Dict[str, Any], message_type: str = "broadcast"):
        """
        Broadcast message to all connected clients
        Automatically removes broken connections
        """
        if not self.active_connections:
            await logger.adebug("No active WebSocket connections for broadcast")
            return
        
        message["broadcast_type"] = message_type
        successful_sends = 0
        failed_connections = []
        
        # Send to all active connections
        for connection_id in list(self.active_connections.keys()):
            success = await self._send_to_connection(connection_id, message)
            if success:
                successful_sends += 1
            else:
                failed_connections.append(connection_id)
        
        # Clean up failed connections
        for failed_id in failed_connections:
            if failed_id in self.active_connections:
                await self.disconnect(failed_id)
        
        await logger.ainfo(
            "WebSocket broadcast completed",
            message_type=message_type,
            successful_sends=successful_sends,
            failed_connections=len(failed_connections),
            active_connections=len(self.active_connections)
        )
    
    async def broadcast_alert(self, alert_data: Dict[str, Any]):
        """
        Broadcast real-time alert to dashboard clients
        High priority alerts get special formatting
        """
        alert_message = {
            "type": "alert_notification",
            "alert": {
                "id": alert_data.get("id"),
                "person_id": alert_data.get("person_id"),
                "camera_id": alert_data.get("camera_id"),
                "confidence_score": alert_data.get("confidence_score"),
                "priority": alert_data.get("priority", "medium"),
                "alert_type": alert_data.get("alert_type", "basic_detection"),
                "triggered_at": alert_data.get("triggered_at"),
                "message": alert_data.get("message"),
                "notification_channels": alert_data.get("notification_channels", []),
                "metadata": alert_data.get("metadata", {})
            },
            "dashboard_display": {
                "show_popup": alert_data.get("priority") in ["high", "critical"],
                "auto_dismiss_seconds": 30 if alert_data.get("priority") == "low" else 0,
                "sound_alert": alert_data.get("priority") in ["critical"],
                "badge_color": self._get_priority_color(alert_data.get("priority", "medium"))
            }
        }
        
        await self.broadcast_to_all(alert_message, "alert_notification")
        
        await logger.ainfo(
            "Real-time alert broadcasted to dashboard",
            alert_id=alert_data.get("id"),
            priority=alert_data.get("priority"),
            active_connections=len(self.active_connections)
        )
    
    async def broadcast_person_sighting(self, sighting_data: Dict[str, Any]):
        """
        Broadcast real-time person sighting to dashboard
        """
        sighting_message = {
            "type": "person_sighting",
            "sighting": {
                "person_id": sighting_data.get("person_id"),
                "camera_id": sighting_data.get("camera_id"),
                "confidence_score": sighting_data.get("confidence_score"),
                "timestamp": sighting_data.get("timestamp"),
                "face_bbox": sighting_data.get("face_bbox"),
                "metadata": sighting_data.get("metadata", {})
            }
        }
        
        await self.broadcast_to_all(sighting_message, "person_sighting")
    
    async def broadcast_system_status(self, status_data: Dict[str, Any]):
        """
        Broadcast system status updates to dashboard
        """
        status_message = {
            "type": "system_status",
            "status": status_data
        }
        
        await self.broadcast_to_all(status_message, "system_status")
    
    def _get_priority_color(self, priority: str) -> str:
        """Get color code for alert priority"""
        priority_colors = {
            "low": "#28a745",      # Green
            "medium": "#ffc107",   # Yellow
            "high": "#fd7e14",     # Orange
            "critical": "#dc3545"  # Red
        }
        return priority_colors.get(priority, "#6c757d")  # Default gray
    
    async def get_connection_stats(self) -> Dict[str, Any]:
        """
        Get current WebSocket connection statistics
        """
        return {
            **self.connection_stats,
            "connection_details": [
                {
                    "connection_id": conn_id,
                    "connected_at": conn_info["connected_at"].isoformat(),
                    "messages_sent": conn_info["messages_sent"],
                    "messages_received": conn_info["messages_received"],
                    "client_info": conn_info["client_info"]
                }
                for conn_id, conn_info in self.active_connections.items()
            ]
        }


# Global WebSocket manager instance
websocket_manager = WebSocketConnectionManager()