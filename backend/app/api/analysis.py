from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.utils.database import get_db
from app.schemas.analysis_schema import (
    FundamentalAnalysisRequest,
    TechnicalAnalysisRequest,
    AnalysisResponse
)
from app.services.analysis_service import AnalysisService
from app.utils.helpers import create_response

router = APIRouter()


@router.post("/fundamental", response_model=dict)
async def fundamental_analysis(
    request: FundamentalAnalysisRequest,
    db: AsyncSession = Depends(get_db)
):
    try:
        service = AnalysisService(db)
        result = await service.fundamental_analysis(request)
        return create_response(result)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/technical", response_model=dict)
async def technical_analysis(
    request: TechnicalAnalysisRequest,
    db: AsyncSession = Depends(get_db)
):
    try:
        service = AnalysisService(db)
        result = await service.technical_analysis(request)
        return create_response(result)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/history/{analysis_id}", response_model=dict)
async def get_analysis_history(
    analysis_id: str,
    db: AsyncSession = Depends(get_db)
):
    try:
        service = AnalysisService(db)
        result = await service.get_analysis_history(analysis_id)
        if not result:
            raise HTTPException(status_code=404, detail="Analysis not found")
        return create_response(result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
