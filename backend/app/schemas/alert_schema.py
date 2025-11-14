from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class AlertCondition(str, Enum):
    PRICE_ABOVE = "PRICE_ABOVE"
    PRICE_BELOW = "PRICE_BELOW"
    PRICE_CHANGE_PERCENT = "PRICE_CHANGE_PERCENT"
    VOLUME_SPIKE = "VOLUME_SPIKE"
    RSI_ABOVE = "RSI_ABOVE"
    RSI_BELOW = "RSI_BELOW"
    MACD_CROSS = "MACD_CROSS"
    DRAWDOWN_THRESHOLD = "DRAWDOWN_THRESHOLD"


class AlertStatus(str, Enum):
    ACTIVE = "ACTIVE"
    TRIGGERED = "TRIGGERED"
    PAUSED = "PAUSED"
    DELETED = "DELETED"


class NotificationChannel(str, Enum):
    EMAIL = "EMAIL"
    SMS = "SMS"
    DISCORD = "DISCORD"
    WEBHOOK = "WEBHOOK"


class AlertCreate(BaseModel):
    userId: int = Field(..., alias="userId")
    symbol: str = Field(..., min_length=3, max_length=20)
    condition: AlertCondition
    threshold: float
    channels: List[NotificationChannel] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AlertResponse(BaseModel):
    id: int
    userId: int
    symbol: str
    condition: str
    threshold: float
    status: str
    channels: List[str]
    createdAt: datetime
    triggeredAt: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class AlertListResponse(BaseModel):
    alerts: List[AlertResponse]
    total: int
    active: int
