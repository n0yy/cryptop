from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List, Dict

from app.schemas.backtest_schema import BacktestRequest
from app.backtesting.engine import BacktestEngine
from app.utils.logger import logger
from app.utils.cache import cache_get, cache_set


class BacktestService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.engine = BacktestEngine()
    
    async def run_backtest(self, request: BacktestRequest) -> Dict:
        try:
            result = await self.engine.run_backtest(
                strategy_name=request.strategyName,
                symbol=request.symbol,
                period=request.period,
                parameters=request.parameters,
                initial_capital=request.initialCapital
            )
            
            await cache_set(f"backtest:{result['backtestId']}", result, ttl=86400)
            
            logger.info(f"Completed backtest {result['backtestId']}")
            
            return result
        
        except Exception as e:
            logger.error(f"Backtest service error: {e}")
            raise
    
    async def get_backtest_results(self, backtest_id: str) -> Optional[Dict]:
        cached = await cache_get(f"backtest:{backtest_id}")
        return cached
    
    async def get_user_backtest_history(self, user_id: int) -> List[Dict]:
        return []
