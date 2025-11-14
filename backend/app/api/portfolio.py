from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.utils.database import get_db
from app.schemas.portfolio_schema import (
    PortfolioCreate,
    PortfolioResponse,
    PositionCreate,
    PositionResponse
)
from app.services.portfolio_service import PortfolioService
from app.utils.helpers import create_response

router = APIRouter()


@router.post("", response_model=dict)
async def create_portfolio(
    portfolio_data: PortfolioCreate,
    db: AsyncSession = Depends(get_db)
):
    try:
        service = PortfolioService(db)
        portfolio = await service.create_portfolio(portfolio_data)
        return create_response(portfolio)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{portfolio_id}", response_model=dict)
async def get_portfolio(
    portfolio_id: int,
    db: AsyncSession = Depends(get_db)
):
    try:
        service = PortfolioService(db)
        portfolio = await service.get_portfolio(portfolio_id)
        if not portfolio:
            raise HTTPException(status_code=404, detail="Portfolio not found")
        return create_response(portfolio)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/user/{user_id}", response_model=dict)
async def get_user_portfolios(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    try:
        service = PortfolioService(db)
        portfolios = await service.get_user_portfolios(user_id)
        return create_response(portfolios)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{portfolio_id}/positions", response_model=dict)
async def add_position(
    portfolio_id: int,
    position_data: PositionCreate,
    db: AsyncSession = Depends(get_db)
):
    try:
        service = PortfolioService(db)
        position = await service.add_position(portfolio_id, position_data)
        return create_response(position)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{portfolio_id}/analysis", response_model=dict)
async def get_portfolio_analysis(
    portfolio_id: int,
    db: AsyncSession = Depends(get_db)
):
    try:
        service = PortfolioService(db)
        analysis = await service.get_portfolio_analysis(portfolio_id)
        if not analysis:
            raise HTTPException(status_code=404, detail="Portfolio not found")
        return create_response(analysis)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{portfolio_id}", response_model=dict)
async def delete_portfolio(
    portfolio_id: int,
    db: AsyncSession = Depends(get_db)
):
    try:
        service = PortfolioService(db)
        success = await service.delete_portfolio(portfolio_id)
        if not success:
            raise HTTPException(status_code=404, detail="Portfolio not found")
        return create_response({"message": "Portfolio deleted successfully"})
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
