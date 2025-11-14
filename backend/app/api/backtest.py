from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.utils.database import get_db
from app.schemas.backtest_schema import BacktestRequest, BacktestResponse
from app.services.backtest_service import BacktestService
from app.utils.helpers import create_response

router = APIRouter()


@router.post("/strategy", response_model=dict)
async def run_backtest(
    request: BacktestRequest,
    db: AsyncSession = Depends(get_db)
):
    try:
        service = BacktestService(db)
        result = await service.run_backtest(request)
        return create_response(result)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/results/{backtest_id}", response_model=dict)
async def get_backtest_results(
    backtest_id: str,
    db: AsyncSession = Depends(get_db)
):
    try:
        service = BacktestService(db)
        result = await service.get_backtest_results(backtest_id)
        if not result:
            raise HTTPException(status_code=404, detail="Backtest not found")
        return create_response(result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/history/{user_id}", response_model=dict)
async def get_backtest_history(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    try:
        service = BacktestService(db)
        results = await service.get_user_backtest_history(user_id)
        return create_response(results)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
