"""
FACEGUARD V2 NOTIFICATION SERVICE - WEBSOCKET API
Rule 2: Zero Placeholder Code - Real WebSocket implementation for dashboard updates
Rule 3: Error-First Development - Comprehensive connection management

WebSocket Real-time Features:
- Live alert notifications
- System status updates
- Notification delivery tracking
- Multi-client broadcasting
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, List, Any, Optional
import json
import asyncio
import structlog
from datetime import datetime
from uuid import uuid4

from storage.database import get_db_session
from domain.schemas import SuccessResponse, ErrorResponse
from config.settings import get_settings

logger = structlog.get_logger(__name__)
router = APIRouter(prefix="/ws", tags=["websocket"])
settings = get_settings()


class WebSocketManager:
    """
    Production WebSocket connection manager
    
    Features:
    - Connection management per room/user
    - Broadcast messaging
    - Connection health monitoring
    - Automatic cleanup
    """
    
    def __init__(self):
        # Active connections by room
        self.active_connections: Dict[str, List[WebSocket]] = {
            "alerts": [],           # Alert notifications
            "notifications": [],    # Notification delivery updates
            "system": [],          # System status updates
            "dashboard": []        # General dashboard updates
        }
        
        # Connection metadata
        self.connection_metadata: Dict[WebSocket, Dict[str, Any]] = {}
        
        # Message queue for offline storage
        self.message_queue: Dict[str, List[Dict[str, Any]]] = {
            "alerts": [],
            "notifications": [],
            "system": [],
            "dashboard": []
        }
        
        self.max_queue_size = 100
    
    async def connect(self, websocket: WebSocket, room: str, client_id: Optional[str] = None):
        """Accept WebSocket connection and add to room"""
        try:
            await websocket.accept()
            
            if room not in self.active_connections:
                self.active_connections[room] = []
            
            self.active_connections[room].append(websocket)
            
            # Store connection metadata
            self.connection_metadata[websocket] = {
                "room": room,
                "client_id": client_id or str(uuid4()),
                "connected_at": datetime.utcnow(),
                "last_ping": datetime.utcnow()
            }
            
            await logger.ainfo("WebSocket connection established",
                             room=room,
                             client_id=client_id,
                             total_connections=len(self.active_connections[room]))
            
            # Send queued messages to new connection
            await self._send_queued_messages(websocket, room)
            
            # Send welcome message
            await self._send_to_connection(websocket, {
                "type": "connection_established",
                "room": room,
                "client_id": self.connection_metadata[websocket]["client_id"],
                "timestamp": datetime.utcnow().isoformat(),
                "queued_messages": len(self.message_queue.get(room, []))
            })
            
        except Exception as e:
            await logger.aerror("WebSocket connection failed", room=room, error=str(e))
            raise
    
    def disconnect(self, websocket: WebSocket):
        """Remove WebSocket connection"""
        try:
            metadata = self.connection_metadata.get(websocket, {})
            room = metadata.get("room", "unknown")
            client_id = metadata.get("client_id", "unknown")
            
            # Remove from active connections
            if room in self.active_connections:
                if websocket in self.active_connections[room]:
                    self.active_connections[room].remove(websocket)
            
            # Remove metadata
            if websocket in self.connection_metadata:
                del self.connection_metadata[websocket]
            
            logger.info("WebSocket disconnected",
                       room=room,
                       client_id=client_id,
                       remaining_connections=len(self.active_connections.get(room, [])))
            
        except Exception as e:
            logger.error("WebSocket disconnect cleanup failed", error=str(e))
    
    async def broadcast_to_room(self, room: str, message: Dict[str, Any]):
        """Broadcast message to all connections in room"""
        try:
            if room not in self.active_connections:
                await logger.awarn("Broadcast to non-existent room", room=room)
                return
            
            # Add to message queue
            self._add_to_queue(room, message)
            
            connections = self.active_connections[room].copy()
            if not connections:
                await logger.adebug("No active connections for broadcast", room=room)
                return
            
            await logger.ainfo("Broadcasting message",
                             room=room,
                             connections=len(connections),
                             message_type=message.get("type", "unknown"))
            
            # Send to all connections
            disconnected = []
            for connection in connections:
                try:
                    await self._send_to_connection(connection, message)
                except Exception as e:
                    await logger.awarn("Failed to send to connection", error=str(e))
                    disconnected.append(connection)
            
            # Clean up disconnected clients
            for connection in disconnected:
                self.disconnect(connection)
                
        except Exception as e:
            await logger.aerror("Broadcast failed", room=room, error=str(e))
    
    async def send_to_client(self, client_id: str, message: Dict[str, Any]):
        """Send message to specific client"""
        try:
            for websocket, metadata in self.connection_metadata.items():
                if metadata.get("client_id") == client_id:
                    await self._send_to_connection(websocket, message)
                    return True
            
            await logger.awarn("Client not found for direct message", client_id=client_id)
            return False
            
        except Exception as e:
            await logger.aerror("Direct message failed", client_id=client_id, error=str(e))
            return False
    
    async def _send_to_connection(self, websocket: WebSocket, message: Dict[str, Any]):
        """Send message to specific WebSocket connection"""
        try:
            # Add timestamp if not present
            if "timestamp" not in message:
                message["timestamp"] = datetime.utcnow().isoformat()
            
            await websocket.send_text(json.dumps(message, default=str))
            
        except Exception as e:
            await logger.aerror("Failed to send WebSocket message", error=str(e))
            raise
    
    async def _send_queued_messages(self, websocket: WebSocket, room: str):
        """Send queued messages to newly connected client"""
        try:
            queued = self.message_queue.get(room, [])
            if not queued:
                return
            
            await logger.ainfo("Sending queued messages",
                             room=room,
                             queued_count=len(queued))
            
            for message in queued:
                await self._send_to_connection(websocket, {
                    **message,
                    "queued": True
                })
                
        except Exception as e:
            await logger.aerror("Failed to send queued messages", room=room, error=str(e))
    
    def _add_to_queue(self, room: str, message: Dict[str, Any]):
        """Add message to queue for offline clients"""
        try:
            if room not in self.message_queue:
                self.message_queue[room] = []
            
            # Add message with queue timestamp
            queued_message = {
                **message,
                "queued_at": datetime.utcnow().isoformat()
            }
            
            self.message_queue[room].append(queued_message)
            
            # Maintain queue size limit
            if len(self.message_queue[room]) > self.max_queue_size:
                self.message_queue[room] = self.message_queue[room][-self.max_queue_size:]
                
        except Exception as e:
            logger.error("Failed to queue message", room=room, error=str(e))
    
    async def get_status(self) -> Dict[str, Any]:
        """Get WebSocket manager status"""
        try:
            return {
                "active_rooms": list(self.active_connections.keys()),
                "total_connections": sum(len(conns) for conns in self.active_connections.values()),
                "connections_by_room": {
                    room: len(conns) for room, conns in self.active_connections.items()
                },
                "queued_messages": {
                    room: len(msgs) for room, msgs in self.message_queue.items()
                },
                "manager_status": "healthy"
            }
        except Exception as e:
            await logger.aerror("Failed to get WebSocket status", error=str(e))
            return {"manager_status": "error", "error": str(e)}


# Global WebSocket manager instance
ws_manager = WebSocketManager()


@router.websocket("/alerts")
async def websocket_alerts(websocket: WebSocket, client_id: Optional[str] = None):
    """
    WebSocket endpoint for real-time alert notifications
    
    Receives:
    - New alert instances
    - Alert status updates
    - Alert acknowledgments/resolutions
    """
    try:
        await ws_manager.connect(websocket, "alerts", client_id)
        
        while True:
            try:
                # Listen for client messages (ping, acknowledgments, etc.)
                data = await websocket.receive_text()
                message = json.loads(data)
                
                if message.get("type") == "ping":
                    await ws_manager._send_to_connection(websocket, {
                        "type": "pong",
                        "timestamp": datetime.utcnow().isoformat()
                    })
                elif message.get("type") == "acknowledge_alert":
                    # Handle alert acknowledgment
                    alert_id = message.get("alert_id")
                    if alert_id:
                        await ws_manager.broadcast_to_room("alerts", {
                            "type": "alert_acknowledged",
                            "alert_id": alert_id,
                            "acknowledged_by": client_id,
                            "timestamp": datetime.utcnow().isoformat()
                        })
                        
            except WebSocketDisconnect:
                break
            except Exception as e:
                await logger.aerror("WebSocket alerts error", error=str(e))
                break
                
    except Exception as e:
        await logger.aerror("WebSocket alerts connection failed", error=str(e))
    finally:
        ws_manager.disconnect(websocket)


@router.websocket("/notifications")
async def websocket_notifications(websocket: WebSocket, client_id: Optional[str] = None):
    """
    WebSocket endpoint for real-time notification delivery updates
    
    Receives:
    - Notification delivery status
    - Delivery confirmations
    - Delivery failures and retries
    """
    try:
        await ws_manager.connect(websocket, "notifications", client_id)
        
        while True:
            try:
                data = await websocket.receive_text()
                message = json.loads(data)
                
                if message.get("type") == "ping":
                    await ws_manager._send_to_connection(websocket, {
                        "type": "pong"
                    })
                    
            except WebSocketDisconnect:
                break
            except Exception as e:
                await logger.aerror("WebSocket notifications error", error=str(e))
                break
                
    except Exception as e:
        await logger.aerror("WebSocket notifications connection failed", error=str(e))
    finally:
        ws_manager.disconnect(websocket)


@router.websocket("/system")
async def websocket_system(websocket: WebSocket, client_id: Optional[str] = None):
    """
    WebSocket endpoint for system status updates
    
    Receives:
    - Service health status
    - Performance metrics
    - System alerts
    """
    try:
        await ws_manager.connect(websocket, "system", client_id)
        
        while True:
            try:
                data = await websocket.receive_text()
                message = json.loads(data)
                
                if message.get("type") == "ping":
                    await ws_manager._send_to_connection(websocket, {
                        "type": "pong"
                    })
                elif message.get("type") == "get_status":
                    # Send current system status
                    status = await ws_manager.get_status()
                    await ws_manager._send_to_connection(websocket, {
                        "type": "system_status",
                        "data": status
                    })
                    
            except WebSocketDisconnect:
                break
            except Exception as e:
                await logger.aerror("WebSocket system error", error=str(e))
                break
                
    except Exception as e:
        await logger.aerror("WebSocket system connection failed", error=str(e))
    finally:
        ws_manager.disconnect(websocket)


@router.websocket("/dashboard")
async def websocket_dashboard(websocket: WebSocket, client_id: Optional[str] = None):
    """
    WebSocket endpoint for general dashboard updates
    
    Receives:
    - Live statistics
    - Activity feeds
    - General notifications
    """
    try:
        await ws_manager.connect(websocket, "dashboard", client_id)
        
        while True:
            try:
                data = await websocket.receive_text()
                message = json.loads(data)
                
                if message.get("type") == "ping":
                    await ws_manager._send_to_connection(websocket, {
                        "type": "pong"
                    })
                elif message.get("type") == "subscribe_updates":
                    # Client requesting specific update types
                    update_types = message.get("updates", [])
                    await ws_manager._send_to_connection(websocket, {
                        "type": "subscription_confirmed",
                        "updates": update_types
                    })
                    
            except WebSocketDisconnect:
                break
            except Exception as e:
                await logger.aerror("WebSocket dashboard error", error=str(e))
                break
                
    except Exception as e:
        await logger.aerror("WebSocket dashboard connection failed", error=str(e))
    finally:
        ws_manager.disconnect(websocket)


# API endpoints for WebSocket management

@router.get("/status")
async def get_websocket_status():
    """Get WebSocket manager status and statistics"""
    try:
        status = await ws_manager.get_status()
        return {
            "status": "operational",
            "websocket_manager": status,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        await logger.aerror("Failed to get WebSocket status", error=str(e))
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


@router.post("/broadcast/{room}")
async def broadcast_message(
    room: str,
    message: Dict[str, Any],
    session: AsyncSession = Depends(get_db_session)
):
    """
    Broadcast message to all clients in a room
    
    For testing and administrative purposes
    """
    try:
        if room not in ws_manager.active_connections:
            return {
                "error": "room_not_found",
                "message": f"Room '{room}' does not exist",
                "available_rooms": list(ws_manager.active_connections.keys())
            }
        
        await ws_manager.broadcast_to_room(room, {
            "type": "admin_broadcast",
            "data": message,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        return {
            "status": "success",
            "room": room,
            "connections_notified": len(ws_manager.active_connections[room]),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        await logger.aerror("Broadcast failed", room=room, error=str(e))
        return {
            "error": "broadcast_failed",
            "message": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


# Helper functions for other services to use

async def broadcast_alert_update(alert_data: Dict[str, Any]):
    """Broadcast alert update to dashboard clients"""
    await ws_manager.broadcast_to_room("alerts", {
        "type": "alert_update",
        "data": alert_data
    })


async def broadcast_notification_update(notification_data: Dict[str, Any]):
    """Broadcast notification update to dashboard clients"""
    await ws_manager.broadcast_to_room("notifications", {
        "type": "notification_update", 
        "data": notification_data
    })


async def broadcast_system_update(system_data: Dict[str, Any]):
    """Broadcast system update to dashboard clients"""
    await ws_manager.broadcast_to_room("system", {
        "type": "system_update",
        "data": system_data
    })


async def get_websocket_manager():
    """Get the global WebSocket manager instance"""
    return ws_manager