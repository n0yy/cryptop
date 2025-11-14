from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

import numpy as np  # For potential future use, but not directly needed here

from app.core.database import get_db
from app.services.risk_management_service import RiskManagementService
from app.services.portfolio_service import PortfolioService
from app.models.position import Position
from app.schemas.portfolio_schema import PositionResponse
from pydantic import BaseModel


router = APIRouter(prefix="/risk", tags=["Risk"])


class PositionSizeRequest(BaseModel):
    risk_tolerance: str
    portfolio_value: float


class PositionSizeResponse(BaseModel):
    recommended_position_size: float


class LiquidationRequest(BaseModel):
    entry_price: float
    quantity: float
    leverage: float
    collateral: float


class LiquidationResponse(BaseModel):
    liquidation_price: float


class RiskUpdateRequest(BaseModel):
    stop_loss_price: Optional[float] = None
    take_profit_price: Optional[float] = None
    leverage: Optional[float] = None
    collateral: Optional[float] = None


class RiskUpdateResponse(BaseModel):
    position_id: int
    updated_fields: list


@router.post("/position-size", response_model=PositionSizeResponse)
async def calculate_position_size(
    request: PositionSizeRequest,
    db: AsyncSession = Depends(get_db)
):
    """Calculate recommended position size based on risk tolerance."""
    try:
        risk_service = RiskManagementService(db)
        position_size = risk_service.calculate_position_size(
            request.risk_tolerance, request.portfolio_value
        )
        return PositionSizeResponse(recommended_position_size=position_size)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/liquidation-price", response_model=LiquidationResponse)
async def calculate_liquidation_price(
    request: LiquidationRequest,
    db: AsyncSession = Depends(get_db)
):
    """Calculate liquidation price for a leveraged position."""
    try:
        risk_service = RiskManagementService(db)
        liquidation_price = risk_service.calculate_liquidation_price(
            request.entry_price,
            request.quantity,
            request.leverage,
            request.collateral
        )
        return LiquidationResponse(liquidation_price=liquidation_price)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/positions/{position_id}/risk", response_model=RiskUpdateResponse)
async def update_position_risk(
    position_id: int,
    request: RiskUpdateRequest,
    db: AsyncSession = Depends(get_db)
):
    """Update stop loss, take profit, leverage, and collateral for a position."""
    from sqlalchemy import update, select
    from app.models.position import Position
    
    result = await db.execute(select(Position).where(Position.id == position_id))
    position = result.scalar_one_or_none()
    
    if not position:
        raise HTTPException(status_code=404, detail="Position not found")
    
    updated_fields = []
    
    if request.stop_loss_price is not None:
        position.stop_loss_price = request.stop_loss_price
        updated_fields.append("stop_loss_price")
    
    if request.take_profit_price is not None:
        position.take_profit_price = request.take_profit_price
        updated_fields.append("take_profit_price")
    
    if request.leverage is not None:
        position.leverage = request.leverage
        updated_fields.append("leverage")
    
    if request.collateral is not None:
        position.collateral = request.collateral
        updated_fields.append("collateral")
    
    if updated_fields:
        await db.commit()
        await db.refresh(position)
    
    return RiskUpdateResponse(
        position_id=position.id,
        updated_fields=updated_fields
    )
