from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, Set
import json
import asyncio

from app.websocket.manager import ConnectionManager
from app.utils.logger import logger

websocket_router = APIRouter()
manager = ConnectionManager()


@websocket_router.websocket("/alerts/{user_id}")
async def websocket_alerts(websocket: WebSocket, user_id: int):
    await manager.connect(websocket, user_id)
    
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("action") == "subscribe":
                symbols = message.get("symbols", [])
                await manager.subscribe_symbols(user_id, symbols)
                await websocket.send_json({
                    "type": "SUBSCRIPTION_CONFIRMED",
                    "symbols": symbols
                })
            
            elif message.get("action") == "unsubscribe":
                symbols = message.get("symbols", [])
                await manager.unsubscribe_symbols(user_id, symbols)
                await websocket.send_json({
                    "type": "UNSUBSCRIPTION_CONFIRMED",
                    "symbols": symbols
                })
            
            elif message.get("action") == "ping":
                await websocket.send_json({"type": "PONG"})
    
    except WebSocketDisconnect:
        manager.disconnect(user_id)
        logger.info(f"WebSocket disconnected for user {user_id}")
    
    except Exception as e:
        logger.error(f"WebSocket error for user {user_id}: {e}")
        manager.disconnect(user_id)


@websocket_router.websocket("/prices")
async def websocket_prices(websocket: WebSocket):
    await websocket.accept()
    
    try:
        while True:
            await asyncio.sleep(1)
            
            price_update = {
                "type": "PRICE_UPDATE",
                "symbol": "BTC-USD",
                "price": 50000.0,
                "timestamp": "2025-11-13T12:00:00Z"
            }
            
            await websocket.send_json(price_update)
    
    except WebSocketDisconnect:
        logger.info("Price WebSocket disconnected")
    
    except Exception as e:
        logger.error(f"Price WebSocket error: {e}")
