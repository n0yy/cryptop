from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from typing import Optional, List, Dict, Tuple
from datetime import datetime
import numpy as np
import pandas as pd
from decimal import Decimal

from app.models.risk_management import StopLossTakeProfitOrder, OrderType, OrderStatus
from app.models.portfolio import Portfolio
from app.models.position import Position
from app.schemas.risk_management_schema import (
    StopLossTakeProfitOrderCreate, StopLossTakeProfitOrderResponse,
    PositionSizingRequest, PositionSizingResponse,
    CorrelationRiskAnalysisRequest, CorrelationRiskAnalysisResponse,
    LiquidationPriceRequest, LiquidationPriceResponse
)
from app.integrations.coingecko import CoinGeckoClient
from app.services.alert_service import AlertService
from app.utils.logger import logger


class RiskManagementService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.coingecko = CoinGeckoClient()
        self.alert_service = AlertService(db)
    
    async def create_stop_loss_take_profit_order(
        self, 
        order_data: StopLossTakeProfitOrderCreate
    ) -> StopLossTakeProfitOrderResponse:
        """Create a new stop loss or take profit order"""
        order = StopLossTakeProfitOrder(
            portfolio_id=order_data.portfolioId,
            symbol=order_data.symbol,
            order_type=order_data.orderType,
            trigger_price=order_data.triggerPrice,
            quantity=order_data.quantity,
            leverage=order_data.leverage
        )
        
        self.db.add(order)
        await self.db.commit()
        await self.db.refresh(order)
        
        logger.info(f"Created {order_data.orderType.value} order {order.id} for portfolio {order_data.portfolioId}")
        
        return StopLossTakeProfitOrderResponse.from_orm(order)
    
    async def get_orders_by_portfolio(self, portfolio_id: int) -> List[StopLossTakeProfitOrderResponse]:
        """Get all orders for a specific portfolio"""
        result = await self.db.execute(
            select(StopLossTakeProfitOrder).where(
                StopLossTakeProfitOrder.portfolio_id == portfolio_id
            ).order_by(StopLossTakeProfitOrder.created_at.desc())
        )
        orders = result.scalars().all()
        return [StopLossTakeProfitOrderResponse.from_orm(order) for order in orders]
    
    async def cancel_order(self, order_id: int) -> bool:
        """Cancel a pending order"""
        result = await self.db.execute(
            select(StopLossTakeProfitOrder).where(StopLossTakeProfitOrder.id == order_id)
        )
        order = result.scalar_one_or_none()
        
        if not order or order.status != OrderStatus.PENDING:
            return False
        
        order.status = OrderStatus.CANCELLED
        await self.db.commit()
        
        logger.info(f"Cancelled order {order_id}")
        return True
    
    async def stop_loss_take_profit_order(
        self, 
        order_id: int
    ) -> Optional[StopLossTakeProfitOrderResponse]:
        """Execute or simulate execution of a stop loss/take profit order"""
        result = await self.db.execute(
            select(StopLossTakeProfitOrder).where(StopLossTakeProfitOrder.id == order_id)
        )
        order = result.scalar_one_or_none()
        
        if not order or order.status != OrderStatus.PENDING:
            return None
        
        # Get current price from CoinGecko
        current_price = await self.coingecko.get_current_price(order.symbol)
        if not current_price:
            logger.error(f"Could not fetch current price for {order.symbol}")
            return None
        
        # Check if order should be triggered
        should_trigger = False
        if order.order_type == OrderType.STOP_LOSS and current_price <= order.trigger_price:
            should_trigger = True
        elif order.order_type == OrderType.TAKE_PROFIT and current_price >= order.trigger_price:
            should_trigger = True
        
        if should_trigger:
            # Update order status and execution details
            order.status = OrderStatus.TRIGGERED
            order.triggered_at = datetime.utcnow()
            order.executed_price = current_price
            await self.db.commit()
            
            logger.info(f"Triggered {order.order_type.value} order {order_id} at price {current_price}")
            
            # TODO: Integrate with actual exchange API for real execution
            # For now, we simulate the execution
            await self._simulate_order_execution(order, current_price)
        
        return StopLossTakeProfitOrderResponse.from_orm(order)
    
    async def _simulate_order_execution(self, order: StopLossTakeProfitOrder, execution_price: float):
        """Simulate the execution of an order (placeholder for real exchange integration)"""
        # This would integrate with exchange APIs like Binance, Coinbase, etc.
        # For now, we just log the simulated execution
        pnl = 0.0
        if order.order_type == OrderType.STOP_LOSS:
            # Calculate loss (simplified)
            pnl = (execution_price - order.trigger_price) * order.quantity
        elif order.order_type == OrderType.TAKE_PROFIT:
            # Calculate profit (simplified)
            pnl = (execution_price - order.trigger_price) * order.quantity
        
        logger.info(f"Simulated execution: PnL = {pnl:.2f} for order {order.id}")
    
    async def position_sizing_calculator(
        self, 
        request: PositionSizingRequest
    ) -> PositionSizingResponse:
        """Calculate optimal position size based on risk tolerance"""
        # Get current price
        current_price = await self.coingecko.get_current_price(request.symbol)
        if not current_price:
            raise ValueError(f"Could not fetch current price for {request.symbol}")
        
        # Get portfolio value
        portfolio_result = await self.db.execute(
            select(Portfolio).where(Portfolio.id == request.portfolioId)
        )
        portfolio = portfolio_result.scalar_one_or_none()
        if not portfolio:
            raise ValueError(f"Portfolio {request.portfolioId} not found")
        
        # Calculate position size
        risk_amount = portfolio.target_allocations.get(request.symbol, 0) * (request.riskTolerancePercent / 100)
        
        # If stop loss provided, calculate position size based on stop loss distance
        if request.stopLossPrice:
            stop_loss_distance = abs(current_price - request.stopLossPrice) / current_price
            recommended_quantity = (risk_amount * current_price) / (stop_loss_distance * current_price)
        else:
            # Default: risk 2% of position
            recommended_quantity = risk_amount / current_price
        
        # Apply leverage if specified
        if request.leverage and request.leverage > 1:
            recommended_quantity *= request.leverage
        
        position_value = recommended_quantity * current_price
        potential_loss = abs(recommended_quantity * (current_price - (request.stopLossPrice or current_price * 0.98)))
        
        return PositionSizingResponse(
            symbol=request.symbol,
            recommendedQuantity=recommended_quantity,
            riskAmount=risk_amount,
            potentialLoss=potential_loss,
            positionValue=position_value,
            leverage=request.leverage,
            riskRewardRatio=None  # Could be calculated if take profit is provided
        )
    
    async def drawdown_alert_monitor(self, portfolio_id: int, drawdown_threshold: float = 0.1) -> Dict:
        """Monitor portfolio drawdown and trigger alerts if threshold exceeded"""
        # Get portfolio positions
        positions_result = await self.db.execute(
            select(Position).where(Position.portfolio_id == portfolio_id)
        )
        positions = positions_result.scalars().all()
        
        if not positions:
            return {"drawdown": 0, "alert_triggered": False}
        
        # Calculate current portfolio value and historical drawdown
        total_value = 0
        peak_value = 0
        current_values = []
        
        for position in positions:
            current_price = await self.coingecko.get_current_price(position.symbol)
            if current_price:
                position_value = float(position.quantity) * current_price
                total_value += position_value
                current_values.append(position_value)
                
                # Calculate peak value (simplified - in reality, track historical peaks)
                entry_value = float(position.quantity) * float(position.entry_price)
                peak_value += max(entry_value, position_value)
        
        if peak_value == 0:
            return {"drawdown": 0, "alert_triggered": False}
        
        # Calculate drawdown
        drawdown = (peak_value - total_value) / peak_value
        
        # Trigger alert if threshold exceeded
        alert_triggered = False
        if drawdown > drawdown_threshold:
            await self.alert_service.create_alert(
                portfolio_id=portfolio_id,
                alert_type="DRAWDOWN_ALERT",
                message=f"Portfolio drawdown of {drawdown:.2%} exceeds threshold of {drawdown_threshold:.2%}",
                severity="HIGH"
            )
            alert_triggered = True
            logger.warning(f"Drawdown alert triggered for portfolio {portfolio_id}: {drawdown:.2%}")
        
        return {
            "drawdown": drawdown,
            "current_value": total_value,
            "peak_value": peak_value,
            "alert_triggered": alert_triggered
        }
    
    async def correlation_risk_analyzer(
        self, 
        request: CorrelationRiskAnalysisRequest
    ) -> CorrelationRiskAnalysisResponse:
        """Analyze asset correlation within a portfolio"""
        # Get portfolio positions
        positions_result = await self.db.execute(
            select(Position).where(Position.portfolio_id == request.portfolioId)
        )
        positions = positions_result.scalars().all()
        
        if len(positions) < 2:
            return CorrelationRiskAnalysisResponse(
                portfolioId=request.portfolioId,
                correlationMatrix={},
                overallCorrelation=0.0,
                diversificationScore=1.0,
                highCorrelationPairs=[],
                recommendations=["Need more assets for correlation analysis"]
            )
        
        # Get historical price data for correlation calculation
        price_data = {}
        for position in positions:
            historical_prices = await self.coingecko.get_price_history(position.symbol, "90d")
            if historical_prices:
                prices = [price[1] for price in historical_prices]  # Extract price values
                price_data[position.symbol] = prices
        
        if len(price_data) < 2:
            return CorrelationRiskAnalysisResponse(
                portfolioId=request.portfolioId,
                correlationMatrix={},
                overallCorrelation=0.0,
                diversificationScore=1.0,
                highCorrelationPairs=[],
                recommendations=["Insufficient price data for correlation analysis"]
            )
        
        # Calculate correlation matrix
        df = pd.DataFrame(price_data)
        correlation_matrix = df.corr()
        
        # Convert to dict format
        corr_dict = {}
        for symbol1 in correlation_matrix.columns:
            corr_dict[symbol1] = {}
            for symbol2 in correlation_matrix.columns:
                corr_dict[symbol1][symbol2] = float(correlation_matrix.loc[symbol1, symbol2])
        
        # Calculate overall correlation (average of all pairwise correlations)
        n = len(correlation_matrix.columns)
        total_correlation = 0
        count = 0
        
        for i in range(n):
            for j in range(i + 1, n):
                total_correlation += abs(correlation_matrix.iloc[i, j])
                count += 1
        
        overall_correlation = total_correlation / count if count > 0 else 0
        
        # Calculate diversification score (inverse of overall correlation)
        diversification_score = 1 - overall_correlation
        
        # Find high correlation pairs (> 0.7)
        high_correlation_pairs = []
        for i in range(n):
            for j in range(i + 1, n):
                corr = correlation_matrix.iloc[i, j]
                if abs(corr) > 0.7:
                    high_correlation_pairs.append({
                        "asset1": correlation_matrix.columns[i],
                        "asset2": correlation_matrix.columns[j],
                        "correlation": float(corr)
                    })
        
        # Generate recommendations
        recommendations = []
        if overall_correlation > 0.7:
            recommendations.append("Portfolio has high correlation - consider adding uncorrelated assets")
        if len(high_correlation_pairs) > 0:
            recommendations.append(f"Found {len(high_correlation_pairs)} highly correlated asset pairs")
        if diversification_score < 0.3:
            recommendations.append("Low diversification - consider rebalancing")
        
        return CorrelationRiskAnalysisResponse(
            portfolioId=request.portfolioId,
            correlationMatrix=corr_dict,
            overallCorrelation=overall_correlation,
            diversificationScore=diversification_score,
            highCorrelationPairs=high_correlation_pairs,
            recommendations=recommendations
        )
    
    async def liquidation_price_calculator(
        self, 
        request: LiquidationPriceRequest
    ) -> LiquidationPriceResponse:
        """Calculate liquidation price for leveraged positions"""
        # Simplified liquidation price calculation
        # Real calculation would depend on exchange-specific formulas
        
        position_value = request.positionSize * request.entryPrice
        
        # Calculate liquidation price (simplified formula)
        # For long positions: liquidation_price = entry_price * (1 - 1/leverage)
        # For short positions: liquidation_price = entry_price * (1 + 1/leverage)
        # We'll assume long positions here
        
        if request.leverage <= 1:
            liquidation_price = 0  # No leverage, no liquidation
        else:
            liquidation_price = request.entryPrice * (1 - 1 / request.leverage)
        
        # Calculate margin call price (typically when margin ratio drops below 0.5)
        margin_call_price = request.entryPrice * (1 - 0.5 / request.leverage) if request.leverage > 1 else None
        
        # Calculate distance to liquidation
        distance_to_liquidation = abs(liquidation_price - request.entryPrice) / request.entryPrice
        
        # Determine risk level
        if distance_to_liquidation < 0.05:  # Less than 5% distance
            risk_level = "CRITICAL"
        elif distance_to_liquidation < 0.15:  # Less than 15% distance
            risk_level = "HIGH"
        elif distance_to_liquidation < 0.30:  # Less than 30% distance
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"
        
        return LiquidationPriceResponse(
            symbol=request.symbol,
            entryPrice=request.entryPrice,
            leverage=request.leverage,
            positionSize=request.positionSize,
            liquidationPrice=liquidation_price,
            marginCallPrice=margin_call_price,
            distanceToLiquidationPercent=distance_to_liquidation,
            riskLevel=risk_level
        )
