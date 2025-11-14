from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.utils.database import get_db
from app.services.content_service import ContentService
from app.utils.helpers import create_response

router = APIRouter()


@router.get("/daily-digest/{user_id}", response_model=dict)
async def get_daily_digest(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    try:
        service = ContentService(db)
        digest = await service.get_daily_digest(user_id)
        return create_response(digest)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/news", response_model=dict)
async def get_crypto_news(
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
):
    try:
        service = ContentService(db)
        news = await service.get_crypto_news(limit)
        return create_response(news)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/educational", response_model=dict)
async def get_educational_content(
    difficulty: str = "BEGINNER",
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
):
    try:
        service = ContentService(db)
        content = await service.get_educational_content(difficulty, limit)
        return create_response(content)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
