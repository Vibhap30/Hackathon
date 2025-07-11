"""
WebSocket Connection Manager
PowerShare Energy Trading Platform
"""

from fastapi import WebSocket
from typing import Dict, List
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections for real-time communication"""
    
    def __init__(self):
        # Store active connections
        self.active_connections: Dict[str, WebSocket] = {}
        # Store connection metadata
        self.connection_info: Dict[str, dict] = {}
    
    async def connect(self, websocket: WebSocket, client_id: str):
        """Accept a new WebSocket connection"""
        try:
            await websocket.accept()
            self.active_connections[client_id] = websocket
            self.connection_info[client_id] = {
                "connected_at": datetime.now(),
                "message_count": 0,
                "last_activity": datetime.now()
            }
            logger.info(f"Client {client_id} connected. Total connections: {len(self.active_connections)}")
            
            # Send welcome message
            await self.send_personal_message({
                "type": "connection",
                "message": "Connected to PowerShare real-time service",
                "client_id": client_id,
                "timestamp": datetime.now().isoformat()
            }, client_id)
            
        except Exception as e:
            logger.error(f"Error connecting client {client_id}: {e}")
    
    def disconnect(self, client_id: str):
        """Remove a client connection"""
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            if client_id in self.connection_info:
                del self.connection_info[client_id]
            logger.info(f"Client {client_id} disconnected. Total connections: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: dict, client_id: str):
        """Send a message to a specific client"""
        if client_id in self.active_connections:
            try:
                websocket = self.active_connections[client_id]
                await websocket.send_text(json.dumps(message))
                
                # Update connection info
                if client_id in self.connection_info:
                    self.connection_info[client_id]["message_count"] += 1
                    self.connection_info[client_id]["last_activity"] = datetime.now()
                    
            except Exception as e:
                logger.error(f"Error sending message to client {client_id}: {e}")
                # Remove disconnected client
                self.disconnect(client_id)
    
    async def broadcast(self, message: dict):
        """Send a message to all connected clients"""
        if not self.active_connections:
            return
        
        disconnected_clients = []
        
        for client_id, websocket in self.active_connections.items():
            try:
                await websocket.send_text(json.dumps(message) if isinstance(message, dict) else message)
                
                # Update connection info
                if client_id in self.connection_info:
                    self.connection_info[client_id]["message_count"] += 1
                    self.connection_info[client_id]["last_activity"] = datetime.now()
                    
            except Exception as e:
                logger.error(f"Error broadcasting to client {client_id}: {e}")
                disconnected_clients.append(client_id)
        
        # Clean up disconnected clients
        for client_id in disconnected_clients:
            self.disconnect(client_id)
    
    async def send_energy_update(self, update_data: dict):
        """Send energy trading updates to all clients"""
        message = {
            "type": "energy_update",
            "data": update_data,
            "timestamp": datetime.now().isoformat()
        }
        await self.broadcast(message)
    
    async def send_iot_update(self, device_id: str, device_data: dict):
        """Send IoT device updates to relevant clients"""
        message = {
            "type": "iot_update",
            "device_id": device_id,
            "data": device_data,
            "timestamp": datetime.now().isoformat()
        }
        await self.broadcast(message)
    
    async def send_ai_notification(self, user_id: str, notification: dict):
        """Send AI agent notifications to specific user"""
        message = {
            "type": "ai_notification",
            "user_id": user_id,
            "data": notification,
            "timestamp": datetime.now().isoformat()
        }
        
        # Send to specific user (if connected) or broadcast
        user_client_id = f"user_{user_id}"
        if user_client_id in self.active_connections:
            await self.send_personal_message(message, user_client_id)
        else:
            await self.broadcast(message)
    
    async def send_community_update(self, community_id: str, update_data: dict):
        """Send community updates to community members"""
        message = {
            "type": "community_update",
            "community_id": community_id,
            "data": update_data,
            "timestamp": datetime.now().isoformat()
        }
        await self.broadcast(message)
    
    async def send_market_update(self, market_data: dict):
        """Send energy market updates to all clients"""
        message = {
            "type": "market_update",
            "data": market_data,
            "timestamp": datetime.now().isoformat()
        }
        await self.broadcast(message)
    
    def get_connection_stats(self) -> dict:
        """Get statistics about current connections"""
        total_connections = len(self.active_connections)
        total_messages = sum(
            info.get("message_count", 0) 
            for info in self.connection_info.values()
        )
        
        return {
            "total_connections": total_connections,
            "total_messages_sent": total_messages,
            "connected_clients": list(self.active_connections.keys()),
            "connection_details": self.connection_info
        }
    
    async def ping_all_clients(self):
        """Send ping to all clients to check connectivity"""
        ping_message = {
            "type": "ping",
            "timestamp": datetime.now().isoformat()
        }
        await self.broadcast(ping_message)
