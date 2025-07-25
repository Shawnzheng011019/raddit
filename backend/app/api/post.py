from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from app.db.session import get_db
from sqlalchemy.orm import Session
from app.models import Post

router = APIRouter()

class PostCreate(BaseModel):
    title: str
    content: str
    author_id: int

class PostResponse(BaseModel):
    id: int
    title: str
    content: str
    author_id: int
    created_at: str

@router.get("/{post_id}", response_model=PostResponse)
async def get_post(
    post_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific post by ID
    
    Args:
        post_id: ID of the post to retrieve
        db: Database session dependency
        
    Returns:
        Post data
    """
    try:
        post = db.query(Post).filter(Post.id == post_id, Post.is_deleted == False).first()
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        return PostResponse(
            id=post.id,
            title=post.title,
            content=post.content,
            author_id=post.author_id,
            created_at=post.created_at.isoformat()
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", response_model=PostResponse)
async def create_post(
    post: PostCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new post
    
    Args:
        post: Post data
        db: Database session dependency
        
    Returns:
        Created post
    """
    try:
        db_post = Post(
            title=post.title,
            content=post.content,
            author_id=post.author_id
        )
        db.add(db_post)
        db.commit()
        db.refresh(db_post)
        return PostResponse(
            id=db_post.id,
            title=db_post.title,
            content=db_post.content,
            author_id=db_post.author_id,
            created_at=db_post.created_at.isoformat()
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))