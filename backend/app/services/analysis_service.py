from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import uuid
from datetime import datetime

from app.schemas.analysis_schema import FundamentalAnalysisRequest, TechnicalAnalysisRequest
from app.analysis.fundamental import FundamentalAnalyzer
from app.analysis.technical import TechnicalAnalyzer
from app.utils.logger import logger
from app.utils.cache import cache_get, cache_set


class AnalysisService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.fundamental_analyzer = FundamentalAnalyzer()
        self.technical_analyzer = TechnicalAnalyzer()
    
    async def fundamental_analysis(self, request: FundamentalAnalysisRequest) -> dict:
        cache_key = f"fundamental:{request.symbol}:{request.timeframe}"
        cached = await cache_get(cache_key)
        
        if cached:
            logger.info(f"Returning cached fundamental analysis for {request.symbol}")
            return cached
        
        analysis_id = f"ANLYS-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
        
        result = await self.fundamental_analyzer.analyze(
            symbol=request.symbol,
            sources=request.sources,
            include_onchain=request.includeOnChain,
            include_sentiment=request.includeSentiment,
            timeframe=request.timeframe
        )
        
        response = {
            "analysisId": analysis_id,
            "symbol": request.symbol,
            "marketCap": result.get("market_cap", 0),
            "volume24h": result.get("volume_24h", 0),
            "onChainMetrics": result.get("onchain_metrics", {}),
            "sentiment": result.get("sentiment", {}),
            "recommendation": result.get("recommendation", "HOLD"),
            "confidence": result.get("confidence", 0.5),
            "generatedAt": datetime.utcnow().isoformat()
        }
        
        await cache_set(cache_key, response, ttl=1800)
        
        logger.info(f"Generated fundamental analysis {analysis_id} for {request.symbol}")
        
        return response
    
    async def technical_analysis(self, request: TechnicalAnalysisRequest) -> dict:
        cache_key = f"technical:{request.symbol}:{':'.join(request.indicators)}:{request.period}"
        cached = await cache_get(cache_key)
        
        if cached:
            logger.info(f"Returning cached technical analysis for {request.symbol}")
            return cached
        
        result = await self.technical_analyzer.analyze(
            symbol=request.symbol,
            indicators=request.indicators,
            timeframes=request.timeframes,
            period=request.period
        )
        
        response = {
            "symbol": request.symbol,
            "timeframe": request.timeframes[0] if request.timeframes else "1d",
            "indicators": result.get("indicators", {}),
            "chartUrl": result.get("chart_url"),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await cache_set(cache_key, response, ttl=300)
        
        logger.info(f"Generated technical analysis for {request.symbol}")
        
        return response
    
    async def get_analysis_history(self, analysis_id: str) -> Optional[dict]:
        cache_key = f"analysis_history:{analysis_id}"
        cached = await cache_get(cache_key)
        
        if cached:
            return cached
        
        return None
