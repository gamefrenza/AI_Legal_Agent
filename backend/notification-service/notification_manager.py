from typing import Dict, Any, List, Optional
from datetime import datetime
from fastapi import WebSocket, WebSocketDisconnect
from pydantic import BaseModel
import json
import asyncio
import uuid
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class NotificationType(str, Enum):
    COMPLIANCE_ISSUE = "compliance_issue"
    DOCUMENT_UPDATE = "document_update"
    SECURITY_ALERT = "security_alert"

class Notification(BaseModel):
    id: str
    type: NotificationType
    severity: str
    message: str
    details: Dict[str, Any]
    timestamp: datetime
    read: bool = False

class NotificationManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}
        self.notification_store: Dict[str, List[Notification]] = {}
    
    async def connect(self, websocket: WebSocket, user_id: str):
        """Connect a user to the notification system"""
        try:
            await websocket.accept()
            if user_id not in self.active_connections:
                self.active_connections[user_id] = []
            self.active_connections[user_id].append(websocket)
        except Exception as e:
            logger.error(f"Error connecting websocket for user {user_id}: {str(e)}")
            raise
    
    async def disconnect(self, websocket: WebSocket, user_id: str):
        """Disconnect a user from the notification system"""
        try:
            if user_id in self.active_connections:
                self.active_connections[user_id].remove(websocket)
                if not self.active_connections[user_id]:
                    del self.active_connections[user_id]
        except Exception as e:
            logger.error(f"Error disconnecting websocket for user {user_id}: {str(e)}")
    
    async def send_notification(
        self,
        user_id: str,
        notification_type: NotificationType,
        severity: str,
        message: str,
        details: Dict[str, Any]
    ):
        """Send a notification to a specific user"""
        try:
            notification = Notification(
                id=str(uuid.uuid4()),
                type=notification_type,
                severity=severity,
                message=message,
                details=details,
                timestamp=datetime.utcnow()
            )
            
            # Store notification
            if user_id not in self.notification_store:
                self.notification_store[user_id] = []
            self.notification_store[user_id].append(notification)
            
            # Send to all active connections for the user
            if user_id in self.active_connections:
                disconnected = []
                for connection in self.active_connections[user_id]:
                    try:
                        await connection.send_json(notification.dict())
                    except WebSocketDisconnect:
                        disconnected.append(connection)
                    except Exception as e:
                        logger.error(f"Error sending notification to user {user_id}: {str(e)}")
                        disconnected.append(connection)
                
                # Clean up disconnected connections
                for connection in disconnected:
                    await self.disconnect(connection, user_id)
        except Exception as e:
            logger.error(f"Error in send_notification for user {user_id}: {str(e)}")
            raise
    
    async def broadcast_notification(
        self,
        notification_type: NotificationType,
        severity: str,
        message: str,
        details: Dict[str, Any]
    ):
        """Broadcast a notification to all connected users"""
        for user_id in self.active_connections.keys():
            await self.send_notification(
                user_id,
                notification_type,
                severity,
                message,
                details
            )
    
    async def get_unread_notifications(self, user_id: str) -> List[Notification]:
        """Get all unread notifications for a user"""
        if user_id not in self.notification_store:
            return []
        return [n for n in self.notification_store[user_id] if not n.read]
    
    async def mark_as_read(self, user_id: str, notification_id: str):
        """Mark a notification as read"""
        if user_id in self.notification_store:
            for notification in self.notification_store[user_id]:
                if notification.id == notification_id:
                    notification.read = True
                    break 