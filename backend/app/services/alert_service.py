from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import Optional, List
from datetime import datetime

from app.models.alert import Alert
from app.schemas.alert_schema import AlertCreate, AlertUpdate
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
