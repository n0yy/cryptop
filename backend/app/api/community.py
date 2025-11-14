from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.utils.database import get_db
from app.schemas.community_schema import PostCreate, PostResponse
from app.services.community_service import CommunityService
from app.utils.helpers import create_response

router = APIRouter()


@router.post("/posts", response_model=dict)
async def create_post(
    post_data: PostCreate,
    db: AsyncSession = Depends(get_db)
):
    try:
        service = CommunityService(db)
        post = await service.create_post(post_data)
        return create_response(post)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/posts", response_model=dict)
async def get_posts(
    limit: int = 20,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    try:
        service = CommunityService(db)
        posts = await service.get_posts(limit, offset)
        return create_response(posts)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/posts/{post_id}", response_model=dict)
async def get_post(
    post_id: int,
    db: AsyncSession = Depends(get_db)
):
    try:
        service = CommunityService(db)
        post = await service.get_post(post_id)
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        return create_response(post)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/posts/{post_id}/upvote", response_model=dict)
async def upvote_post(
    post_id: int,
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    try:
        service = CommunityService(db)
        result = await service.upvote_post(post_id, user_id)
        return create_response(result)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
