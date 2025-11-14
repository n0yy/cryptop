from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List

from app.models.portfolio import Portfolio
from app.models.position import Position
from app.schemas.portfolio_schema import PortfolioCreate, PositionCreate
from app.portfolio.manager import PortfolioManager
from app.utils.logger import logger


class PortfolioService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.manager = PortfolioManager(db)
    
    async def create_portfolio(self, portfolio_data: PortfolioCreate) -> dict:
        portfolio = Portfolio(
            user_id=portfolio_data.userId,
            name=portfolio_data.name,
            risk_profile=portfolio_data.riskProfile,
            target_allocations=portfolio_data.targetAllocations
        )
        
        self.db.add(portfolio)
        await self.db.commit()
        await self.db.refresh(portfolio)
        
        logger.info(f"Created portfolio {portfolio.id} for user {portfolio.user_id}")
        
        return {
            "portfolioId": portfolio.id,
            "name": portfolio.name,
            "riskProfile": portfolio.risk_profile,
            "currentValue": 0,
            "positions": [],
            "createdAt": portfolio.created_at.isoformat()
        }
    
    async def get_portfolio(self, portfolio_id: int) -> Optional[dict]:
        result = await self.db.execute(
            select(Portfolio).where(Portfolio.id == portfolio_id)
        )
        portfolio = result.scalar_one_or_none()
        
        if not portfolio:
            return None
        
        positions_result = await self.db.execute(
            select(Position).where(Position.portfolio_id == portfolio_id)
        )
        positions = positions_result.scalars().all()
        
        return {
            "portfolioId": portfolio.id,
            "name": portfolio.name,
            "riskProfile": portfolio.risk_profile,
            "targetAllocations": portfolio.target_allocations,
            "positions": [
                {
                    "positionId": p.id,
                    "symbol": p.symbol,
                    "quantity": float(p.quantity),
                    "entryPrice": float(p.entry_price)
                }
                for p in positions
            ],
            "createdAt": portfolio.created_at.isoformat()
        }
    
    async def get_user_portfolios(self, user_id: int) -> List[dict]:
        result = await self.db.execute(
            select(Portfolio).where(Portfolio.user_id == user_id)
        )
        portfolios = result.scalars().all()
        
        return [
            {
                "portfolioId": p.id,
                "name": p.name,
                "riskProfile": p.risk_profile,
                "createdAt": p.created_at.isoformat()
            }
            for p in portfolios
        ]
    
    async def add_position(self, portfolio_id: int, position_data: PositionCreate) -> dict:
        position = Position(
            portfolio_id=portfolio_id,
            symbol=position_data.symbol,
            quantity=position_data.quantity,
            entry_price=position_data.entryPrice,
            entry_date=position_data.entryDate
        )
        
        self.db.add(position)
        await self.db.commit()
        await self.db.refresh(position)
        
        logger.info(f"Added position {position.id} to portfolio {portfolio_id}")
        
        return {
            "positionId": position.id,
            "portfolioId": portfolio_id,
            "symbol": position.symbol,
            "quantity": float(position.quantity),
            "entryPrice": float(position.entry_price),
            "entryDate": position.entry_date.isoformat()
        }
    
    async def get_portfolio_analysis(self, portfolio_id: int) -> Optional[dict]:
        portfolio = await self.get_portfolio(portfolio_id)
        
        if not portfolio:
            return None
        
        analysis = await self.manager.analyze_portfolio(portfolio_id)
        
        return analysis
    
    async def delete_portfolio(self, portfolio_id: int) -> bool:
        result = await self.db.execute(
            select(Portfolio).where(Portfolio.id == portfolio_id)
        )
        portfolio = result.scalar_one_or_none()
        
        if not portfolio:
            return False
        
        await self.db.delete(portfolio)
        await self.db.commit()
        
        logger.info(f"Deleted portfolio {portfolio_id}")
        
        return True
