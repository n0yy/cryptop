from fastapi import WebSocket
from typing import Dict, Set, List
import json

from app.utils.logger import logger


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, WebSocket] = {}
        self.user_subscriptions: Dict[int, Set[str]] = {}
    
    async def connect(self, websocket: WebSocket, user_id: int):
        await websocket.accept()
        self.active_connections[user_id] = websocket
        self.user_subscriptions[user_id] = set()
        logger.info(f"User {user_id} connected via WebSocket")
    
    def disconnect(self, user_id: int):
        if user_id in self.active_connections:
            del self.active_connections[user_id]
        if user_id in self.user_subscriptions:
            del self.user_subscriptions[user_id]
        logger.info(f"User {user_id} disconnected from WebSocket")
    
    async def subscribe_symbols(self, user_id: int, symbols: List[str]):
        if user_id in self.user_subscriptions:
            self.user_subscriptions[user_id].update(symbols)
            logger.info(f"User {user_id} subscribed to {symbols}")
    
    async def unsubscribe_symbols(self, user_id: int, symbols: List[str]):
        if user_id in self.user_subscriptions:
            self.user_subscriptions[user_id].difference_update(symbols)
            logger.info(f"User {user_id} unsubscribed from {symbols}")
    
    async def send_personal_message(self, user_id: int, message: dict):
        if user_id in self.active_connections:
            try:
                await self.active_connections[user_id].send_json(message)
            except Exception as e:
                logger.error(f"Error sending message to user {user_id}: {e}")
                self.disconnect(user_id)
    
    async def broadcast(self, message: dict):
        disconnected_users = []
        
        for user_id, connection in self.active_connections.items():
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting to user {user_id}: {e}")
                disconnected_users.append(user_id)
        
        for user_id in disconnected_users:
            self.disconnect(user_id)
    
    async def broadcast_to_symbol_subscribers(self, symbol: str, message: dict):
        for user_id, subscriptions in self.user_subscriptions.items():
            if symbol in subscriptions:
                await self.send_personal_message(user_id, message)
    
    def get_connection_count(self) -> int:
        return len(self.active_connections)
