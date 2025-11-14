from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class PostCreate(BaseModel):
    userId: int = Field(..., description="User ID")
    title: str = Field(..., description="Post title")
    content: str = Field(..., description="Post content")
    tags: List[str] = Field(default=[], description="Post tags")
    attachments: List[str] = Field(default=[], description="Attachment URLs")


class PostResponse(BaseModel):
    postId: int
    userId: int
    title: str
    upvotes: int
    comments: int
    visibility: str
    createdAt: datetime
    
    class Config:
        from_attributes = True
