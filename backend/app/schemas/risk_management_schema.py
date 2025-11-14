from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from datetime import datetime
from enum import Enum


class OrderType(str, Enum):
    STOP_LOSS = "STOP_LOSS"
    TAKE_PROFIT = "TAKE_PROFIT"


class OrderStatus(str, Enum):
    PENDING = "PENDING"
    ACTIVE = "ACTIVE"
    TRIGGERED = "TRIGGERED"
    CANCELLED = "CANCELLED"


class StopLossTakeProfitOrderCreate(BaseModel):
    portfolioId: int
    symbol: str = Field(..., min_length=3, max_length=20)
    orderType: OrderType
    triggerPrice: float = Field(..., gt=0)
    quantity: float = Field(..., gt=0)
    leverage: Optional[float] = Field(None, gt=0)


class StopLossTakeProfitOrderResponse(BaseModel):
    orderId: int
    portfolioId: int
    symbol: str
    orderType: str
    triggerPrice: float
    quantity: float
    leverage: Optional[float]
    status: str
    createdAt: datetime
    triggeredAt: Optional[datetime]
    executedPrice: Optional[float]
    
    class Config:
        from_attributes = True


class PositionSizingRequest(BaseModel):
    portfolioId: int
    symbol: str = Field(..., min_length=3, max_length=20)
    riskTolerancePercent: float = Field(..., gt=0, le=100)
    stopLossPrice: Optional[float] = Field(None, gt=0)
    leverage: Optional[float] = Field(None, gt=0)


class PositionSizingResponse(BaseModel):
    symbol: str
    recommendedQuantity: float
    riskAmount: float
    potentialLoss: float
    positionValue: float
    leverage: Optional[float]
    riskRewardRatio: Optional[float]


class CorrelationRiskAnalysisRequest(BaseModel):
    portfolioId: int


class CorrelationRiskAnalysisResponse(BaseModel):
    portfolioId: int
    correlationMatrix: Dict[str, Dict[str, float]]
    overallCorrelation: float
    diversificationScore: float
    highCorrelationPairs: List[Dict[str, str]]
    recommendations: List[str]


class LiquidationPriceRequest(BaseModel):
    symbol: str = Field(..., min_length=3, max_length=20)
    entryPrice: float = Field(..., gt=0)
    leverage: float = Field(..., gt=0)
    positionSize: float = Field(..., gt=0)
    walletBalance: float = Field(..., ge=0)


class LiquidationPriceResponse(BaseModel):
    symbol: str
    entryPrice: float
    leverage: float
    positionSize: float
    liquidationPrice: float
    marginCallPrice: Optional[float]
    distanceToLiquidationPercent: float
    riskLevel: str
