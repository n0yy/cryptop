from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from datetime import datetime
from enum import Enum


class RiskProfile(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class PortfolioCreate(BaseModel):
    userId: int
    name: str = Field(..., min_length=1, max_length=100)
    riskProfile: RiskProfile
    targetAllocations: Dict[str, float] = Field(default_factory=dict)


class PortfolioResponse(BaseModel):
    portfolioId: int
    name: str
    riskProfile: str
    currentValue: float = 0
    positions: List[Dict] = Field(default_factory=list)
    createdAt: datetime
    
    class Config:
        from_attributes = True


class PositionCreate(BaseModel):
    symbol: str = Field(..., min_length=3, max_length=20)
    quantity: float = Field(..., gt=0)
    entryPrice: float = Field(..., gt=0)
    entryDate: datetime
    stopLossPrice: Optional[float] = None
    takeProfitPrice: Optional[float] = None
    leverage: Optional[float] = None
    collateral: Optional[float] = None


class PositionResponse(BaseModel):
    positionId: int
    portfolioId: int
    symbol: str
    quantity: float
    entryPrice: float
    currentPrice: Optional[float] = None
    currentValue: Optional[float] = None
    pnl: Optional[float] = None
    pnlPercent: Optional[float] = None
    stopLossPrice: Optional[float] = None
    takeProfitPrice: Optional[float] = None
    leverage: Optional[float] = None
    collateral: Optional[float] = None
    
    class Config:
        from_attributes = True


class PortfolioAnalysisResponse(BaseModel):
    portfolioId: int
    totalValue: float
    totalPnL: float
    allocation: Dict[str, float]
    allocationDeviation: Dict[str, float]
    riskMetrics: Dict[str, float]
    rebalancingNeeded: bool
    alerts: List[str] = Field(default_factory=list)
