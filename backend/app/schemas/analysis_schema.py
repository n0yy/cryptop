from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime
from enum import Enum


class DataSource(str, Enum):
    COINGECKO = "COINGECKO"
    COINMARKETCAP = "COINMARKETCAP"
    ETHERSCAN = "ETHERSCAN"
    BINANCE = "BINANCE"


class Timeframe(str, Enum):
    ONE_HOUR = "1h"
    FOUR_HOUR = "4h"
    ONE_DAY = "1d"
    ONE_WEEK = "1w"
    ONE_MONTH = "1M"


class Recommendation(str, Enum):
    STRONG_BUY = "STRONG_BUY"
    BUY = "BUY"
    HOLD = "HOLD"
    SELL = "SELL"
    STRONG_SELL = "STRONG_SELL"


class FundamentalAnalysisRequest(BaseModel):
    symbol: str = Field(..., min_length=3, max_length=20)
    sources: List[DataSource] = Field(default_factory=lambda: [DataSource.COINGECKO])
    includeOnChain: bool = True
    includeSentiment: bool = True
    timeframe: str = "30d"


class OnChainMetrics(BaseModel):
    activeAddresses: Optional[int] = None
    whaleMovements: Optional[int] = None
    tvl: Optional[float] = None


class SentimentMetrics(BaseModel):
    score: float = Field(..., ge=-1, le=1)
    fearGreedIndex: Optional[int] = Field(None, ge=0, le=100)
    socialVolume: Optional[int] = None


class FundamentalAnalysisResponse(BaseModel):
    analysisId: str
    symbol: str
    marketCap: Optional[float] = None
    volume24h: Optional[float] = None
    onChainMetrics: Optional[OnChainMetrics] = None
    sentiment: Optional[SentimentMetrics] = None
    recommendation: Recommendation
    confidence: float = Field(..., ge=0, le=1)
    generatedAt: datetime


class TechnicalAnalysisRequest(BaseModel):
    symbol: str = Field(..., min_length=3, max_length=20)
    indicators: List[str] = Field(..., min_items=1)
    timeframes: List[Timeframe] = Field(default_factory=lambda: [Timeframe.ONE_DAY])
    period: str = "90d"


class IndicatorResult(BaseModel):
    value: Optional[float] = None
    signal: Optional[str] = None
    trend: Optional[str] = None
    histogram: Optional[float] = None
    upper: Optional[float] = None
    middle: Optional[float] = None
    lower: Optional[float] = None
    position: Optional[str] = None


class TechnicalAnalysisResponse(BaseModel):
    symbol: str
    timeframe: str
    indicators: Dict[str, IndicatorResult]
    chartUrl: Optional[str] = None
    timestamp: datetime
