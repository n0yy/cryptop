from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import datetime

from app.utils.database import get_db
from app.schemas.alert_schema import AlertCreate, AlertResponse, AlertListResponse, AlertUpdate
from app.services.alert_service import AlertService
from app.utils.helpers import create_response, create_error_response

router = APIRouter()


@router.post("", response_model=dict)
async def create_alert(
    alert_data: AlertCreate,
    db: AsyncSession = Depends(get_db)
):
    try:
        service = AlertService(db)
        alert = await service.create_alert(alert_data)
        return create_response(alert)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{user_id}", response_model=dict)
async def get_user_alerts(
    user_id: int,
    status: Optional[str] = Query(None),
    symbol: Optional[str] = Query(None),
    from_date: Optional[datetime] = Query(None, alias="from"),
    to_date: Optional[datetime] = Query(None, alias="to"),
    db: AsyncSession = Depends(get_db)
):
    try:
        service = AlertService(db)
        alerts = await service.get_user_alerts(
            user_id=user_id,
            status=status,
            symbol=symbol,
            from_date=from_date,
            to_date=to_date
        )
        return create_response(alerts)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/detail/{alert_id}", response_model=dict)
async def get_alert(
    alert_id: int,
    db: AsyncSession = Depends(get_db)
):
    try:
        service = AlertService(db)
        alert = await service.get_alert(alert_id)
        if not alert:
            raise HTTPException(status_code=404, detail="Alert not found")
        return create_response(alert)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{alert_id}", response_model=dict)
async def update_alert(
    alert_id: int,
    alert_data: AlertUpdate,
    db: AsyncSession = Depends(get_db)
):
    try:
        service = AlertService(db)
        alert = await service.update_alert(alert_id, alert_data)
        if not alert:
            raise HTTPException(status_code=404, detail="Alert not found")
        return create_response(alert)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{alert_id}", response_model=dict)
async def delete_alert(
    alert_id: int,
    db: AsyncSession = Depends(get_db)
):
    try:
        service = AlertService(db)
        success = await service.delete_alert(alert_id)
        if not success:
            raise HTTPException(status_code=404, detail="Alert not found")
        return create_response({"message": "Alert deleted successfully"})
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
