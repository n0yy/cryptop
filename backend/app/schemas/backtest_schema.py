from pydantic import BaseModel, Field
from typing import Dict, Optional
from datetime import datetime


class BacktestRequest(BaseModel):
    strategyName: str = Field(..., min_length=1)
    symbol: str = Field(..., min_length=3, max_length=20)
    period: str = "1y"
    parameters: Dict[str, float] = Field(default_factory=dict)
    initialCapital: float = Field(default=10000, gt=0)


class BacktestResults(BaseModel):
    totalReturn: float
    sharpeRatio: float
    maxDrawdown: float
    winRate: float
    totalTrades: int
    profitFactor: float


class BacktestResponse(BaseModel):
    backtestId: str
    strategyName: str
    results: BacktestResults
    equityCurveUrl: Optional[str] = None
    completedAt: datetime
