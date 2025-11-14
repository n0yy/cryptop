from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.utils.database import get_db
from app.schemas.risk_management_schema import (
    StopLossTakeProfitOrderCreate, StopLossTakeProfitOrderResponse,
    PositionSizingRequest, PositionSizingResponse,
    CorrelationRiskAnalysisRequest, CorrelationRiskAnalysisResponse,
    LiquidationPriceRequest, LiquidationPriceResponse
)
from app.services.risk_management_service import RiskManagementService
from app.utils.helpers import create_response

router = APIRouter()


@router.post("/orders", response_model=dict)
async def create_stop_loss_take_profit_order(
    order_data: StopLossTakeProfitOrderCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new stop loss or take profit order"""
    try:
        service = RiskManagementService(db)
        order = await service.create_stop_loss_take_profit_order(order_data)
        return create_response(order)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/orders/{portfolio_id}", response_model=dict)
async def get_portfolio_orders(
    portfolio_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get all orders for a specific portfolio"""
    try:
        service = RiskManagementService(db)
        orders = await service.get_orders_by_portfolio(portfolio_id)
        return create_response(orders)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/orders/{order_id}/execute", response_model=dict)
async def execute_order(
    order_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Execute or check if a stop loss/take profit order should be triggered"""
    try:
        service = RiskManagementService(db)
        order = await service.stop_loss_take_profit_order(order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found or cannot be executed")
        return create_response(order)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/orders/{order_id}", response_model=dict)
async def cancel_order(
    order_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Cancel a pending order"""
    try:
        service = RiskManagementService(db)
        success = await service.cancel_order(order_id)
        if not success:
            raise HTTPException(status_code=404, detail="Order not found or cannot be cancelled")
        return create_response({"message": "Order cancelled successfully"})
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/position-sizing", response_model=dict)
async def calculate_position_sizing(
    request: PositionSizingRequest,
    db: AsyncSession = Depends(get_db)
):
    """Calculate optimal position size based on risk tolerance"""
    try:
        service = RiskManagementService(db)
        sizing = await service.position_sizing_calculator(request)
        return create_response(sizing)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/correlation-analysis", response_model=dict)
async def analyze_correlation_risk(
    request: CorrelationRiskAnalysisRequest,
    db: AsyncSession = Depends(get_db)
):
    """Analyze asset correlation within a portfolio"""
    try:
        service = RiskManagementService(db)
        analysis = await service.correlation_risk_analyzer(request)
        return create_response(analysis)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/liquidation-price", response_model=dict)
async def calculate_liquidation_price(
    request: LiquidationPriceRequest,
    db: AsyncSession = Depends(get_db)
):
    """Calculate liquidation price for leveraged positions"""
    try:
        service = RiskManagementService(db)
        liquidation = await service.liquidation_price_calculator(request)
        return create_response(liquidation)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/drawdown-monitor/{portfolio_id}", response_model=dict)
async def monitor_drawdown(
    portfolio_id: int,
    drawdown_threshold: float = 0.1,
    db: AsyncSession = Depends(get_db)
):
    """Monitor portfolio drawdown and trigger alerts if threshold exceeded"""
    try:
        service = RiskManagementService(db)
        result = await service.drawdown_alert_monitor(portfolio_id, drawdown_threshold)
        return create_response(result)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
