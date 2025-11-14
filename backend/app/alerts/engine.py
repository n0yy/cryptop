from typing import List, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from decimal import Decimal

from app.models.alert import Alert
from app.alerts.notifier import AlertNotifier
from app.integrations.coingecko import CoinGeckoClient
from app.utils.logger import logger


class AlertEngine:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.notifier = AlertNotifier()
        self.coingecko = CoinGeckoClient()
    
    async def check_alerts(self) -> int:
        result = await self.db.execute(
            select(Alert).where(Alert.status == "ACTIVE")
        )
        active_alerts = result.scalars().all()
        
        triggered_count = 0
        
        for alert in active_alerts:
            if await self._evaluate_alert(alert):
                await self._trigger_alert(alert)
                triggered_count += 1
        
        logger.info(f"Checked {len(active_alerts)} alerts, triggered {triggered_count}")
        
        return triggered_count
    
    async def _evaluate_alert(self, alert: Alert) -> bool:
        try:
            current_price = await self.coingecko.get_current_price(alert.symbol)
            
            if current_price is None:
                return False
            
            threshold = float(alert.threshold)
            
            if alert.condition == "PRICE_ABOVE" and current_price > threshold:
                return True
            elif alert.condition == "PRICE_BELOW" and current_price < threshold:
                return True
            elif alert.condition == "PRICE_EQUALS" and abs(current_price - threshold) < (threshold * 0.01):
                return True
            elif alert.condition == "PERCENT_CHANGE_ABOVE":
                return False
            elif alert.condition == "PERCENT_CHANGE_BELOW":
                return False
            
            return False
        
        except Exception as e:
            logger.error(f"Error evaluating alert {alert.id}: {e}")
            return False
    
    async def _trigger_alert(self, alert: Alert):
        try:
            current_price = await self.coingecko.get_current_price(alert.symbol)
            
            message = {
                "alertId": alert.id,
                "symbol": alert.symbol,
                "condition": alert.condition,
                "threshold": float(alert.threshold),
                "currentPrice": current_price,
                "message": f"{alert.symbol} {alert.condition} {alert.threshold} (Current: {current_price})"
            }
            
            await self.notifier.send_notification(
                user_id=alert.user_id,
                channels=alert.channels,
                message=message
            )
            
            alert.status = "TRIGGERED"
            alert.triggered_at = func.now()
            await self.db.commit()
            
            logger.info(f"Triggered alert {alert.id} for user {alert.user_id}")
        
        except Exception as e:
            logger.error(f"Error triggering alert {alert.id}: {e}")
