from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, update
from typing import Optional, List
from datetime import datetime

import json

from app.models.alert import Alert
from app.models.position import Position
from app.models.portfolio import Portfolio
from app.schemas.alert_schema import AlertCreate, AlertUpdate
from app.integrations.coingecko import CoinGeckoClient
from app.services.portfolio_service import PortfolioService
from app.utils.logger import logger


class AlertService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_alert(self, alert_data: AlertCreate) -> dict:
        alert = Alert(
            user_id=alert_data.userId,
            symbol=alert_data.symbol,
            condition=alert_data.condition,
            threshold=alert_data.threshold,
            channels=alert_data.channels,
            metadata=str(alert_data.metadata) if alert_data.metadata else None,
            status="ACTIVE"
        )
        
        self.db.add(alert)
        await self.db.commit()
        await self.db.refresh(alert)
        
        logger.info(f"Created alert {alert.id} for user {alert.user_id}")
        
        return {
            "id": alert.id,
            "userId": alert.user_id,
            "symbol": alert.symbol,
            "condition": alert.condition,
            "threshold": float(alert.threshold),
            "status": alert.status,
            "channels": alert.channels,
            "createdAt": alert.created_at.isoformat()
        }
    
    async def get_user_alerts(
        self,
        user_id: int,
        status: Optional[str] = None,
        symbol: Optional[str] = None,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None
    ) -> dict:
        query = select(Alert).where(Alert.user_id == user_id)
        
        if status:
            query = query.where(Alert.status == status)
        if symbol:
            query = query.where(Alert.symbol == symbol)
        if from_date:
            query = query.where(Alert.created_at >= from_date)
        if to_date:
            query = query.where(Alert.created_at <= to_date)
        
        result = await self.db.execute(query)
        alerts = result.scalars().all()
        
        active_count = sum(1 for a in alerts if a.status == "ACTIVE")
        
        return {
            "alerts": [
                {
                    "id": a.id,
                    "symbol": a.symbol,
                    "condition": a.condition,
                    "threshold": float(a.threshold),
                    "status": a.status,
                    "triggeredAt": a.triggered_at.isoformat() if a.triggered_at else None
                }
                for a in alerts
            ],
            "total": len(alerts),
            "active": active_count
        }
    
    async def get_alert(self, alert_id: int) -> Optional[dict]:
        result = await self.db.execute(
            select(Alert).where(Alert.id == alert_id)
        )
        alert = result.scalar_one_or_none()
        
        if not alert:
            return None
        
        return {
            "id": alert.id,
            "userId": alert.user_id,
            "symbol": alert.symbol,
            "condition": alert.condition,
            "threshold": float(alert.threshold),
            "status": alert.status,
            "channels": alert.channels,
            "createdAt": alert.created_at.isoformat()
        }
    
    async def update_alert(self, alert_id: int, alert_data: AlertUpdate) -> Optional[dict]:
        result = await self.db.execute(
            select(Alert).where(Alert.id == alert_id)
        )
        alert = result.scalar_one_or_none()
        
        if not alert:
            return None
        
        if alert_data.threshold is not None:
            alert.threshold = alert_data.threshold
        if alert_data.status is not None:
            alert.status = alert_data.status
        if alert_data.channels is not None:
            alert.channels = alert_data.channels
        
        await self.db.commit()
        await self.db.refresh(alert)
        
        logger.info(f"Updated alert {alert_id}")
        
        return await self.get_alert(alert_id)
    
    async def delete_alert(self, alert_id: int) -> bool:
        result = await self.db.execute(
            select(Alert).where(Alert.id == alert_id)
        )
        alert = result.scalar_one_or_none()
        
        if not alert:
            return False
        
        await self.db.delete(alert)
        await self.db.commit()
        
        logger.info(f"Deleted alert {alert_id}")
        
        return True

    async def trigger_alert(self, alert_id: int) -> bool:
        """Trigger an alert by updating its status and timestamp."""
        result = await self.db.execute(
            select(Alert).where(Alert.id == alert_id)
        )
        alert = result.scalar_one_or_none()
        
        if not alert or alert.status != "ACTIVE":
            return False
        
        alert.status = "TRIGGERED"
        alert.triggered_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(alert)
        
        logger.info(f"Triggered alert {alert_id} for user {alert.user_id}")
        
        # TODO: Implement notification sending based on alert.channels
        
        return True

    async def check_and_trigger_all_risk_alerts(self):
        """Periodically check and trigger risk-related alerts."""
        from sqlalchemy import select
        from app.models.alert import Alert
        from app.integrations.coingecko import CoinGeckoClient
        from app.services.portfolio_service import PortfolioService
        
        query = select(Alert).where(
            Alert.status == "ACTIVE",
            Alert.condition.in_( ["STOP_LOSS", "TAKE_PROFIT", "DRAWDOWN_THRESHOLD"])
        )
        result = await self.db.execute(query)
        alerts = result.scalars().all()
        
        coingecko = CoinGeckoClient()
        portfolio_service = PortfolioService(self.db)
        
        triggered_count = 0
        for alert in alerts:
            condition_met = False
            execution_details = None
            if alert.condition in ["STOP_LOSS", "TAKE_PROFIT"]:
                current_price = await coingecko.get_current_price(alert.symbol)
                if current_price is None:
                    continue
                if alert.condition == "STOP_LOSS" and current_price <= alert.threshold:
                    condition_met = True
                    action = "STOP_LOSS"
                elif alert.condition == "TAKE_PROFIT" and current_price >= alert.threshold:
                    condition_met = True
                    action = "TAKE_PROFIT"
                
                if condition_met:
                    # Find and close the corresponding position
                    pos_query = select(Position).join(Portfolio).where(
                        and_(
                            Portfolio.user_id == alert.user_id,
                            Position.symbol == alert.symbol,
                            Position.quantity > 0
                        )
                    )
                    pos_result = await self.db.execute(pos_query)
                    positions = pos_result.scalars().all()
                    
                    if positions:
                        closed_positions = []
                        for position in positions:
                            old_quantity = position.quantity
                            position.quantity = 0
                            closed_positions.append({
                                "position_id": position.id,
                                "old_quantity": float(old_quantity),
                                "closed_at": datetime.utcnow().isoformat()
                            })
                            logger.info(f"Executed {action} for position {position.id} (symbol: {alert.symbol}) - closed quantity from {old_quantity} to 0")
                        
                        await self.db.commit()
                        
                        execution_details = {
                            "action": action,
                            "current_price": float(current_price),
                            "threshold": float(alert.threshold),
                            "closed_positions": closed_positions
                        }
            elif alert.condition == "DRAWDOWN_THRESHOLD":
                user_portfolios = await portfolio_service.get_user_portfolios(alert.user_id)
                if not user_portfolios:
                    continue
                total_entry_value = 0.0
                total_current_value = 0.0
                for user_port in user_portfolios:
                    portfolio_id = user_port["portfolioId"]
                    # Calculate entry value from positions
                    portfolio = await portfolio_service.get_portfolio(portfolio_id)
                    if portfolio and "positions" in portfolio:
                        for pos in portfolio["positions"]:
                            total_entry_value += pos["quantity"] * pos["entryPrice"]
                    # Get current value from analysis
                    analysis = await portfolio_service.get_portfolio_analysis(portfolio_id)
                    if analysis and "totalValue" in analysis:
                        total_current_value += analysis["totalValue"]
                if total_entry_value > 0:
                    drawdown_percent = ((total_current_value - total_entry_value) / total_entry_value) * 100
                    if drawdown_percent <= -alert.threshold:
                        condition_met = True
                        execution_details = {
                            "action": "DRAWDOWN_ALERT",
                            "drawdown_percent": round(drawdown_percent, 2),
                            "threshold": float(alert.threshold)
                        }
            
            if condition_met:
                # Update alert with execution details in metadata
                current_metadata = json.loads(alert.metadata) if alert.metadata else {}
                current_metadata["execution_details"] = execution_details
                alert.metadata = json.dumps(current_metadata)
                
                if await self.trigger_alert(alert.id):
                    await self.db.commit()  # Commit metadata update
                    triggered_count += 1
        logger.info(f"Risk check completed. Triggered {triggered_count} alerts.")
        return triggered_count
EOF'