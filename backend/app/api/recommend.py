from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from app.services import recall_service, rank_service
from app.db.session import get_db
from sqlalchemy.orm import Session

router = APIRouter()

# Pydantic models for request/response
class PostResponse(BaseModel):
    id: int
    title: str
    content: str
    author: str
    timestamp: str

class RecommendationResponse(BaseModel):
    posts: List[PostResponse]

@router.get("/home", response_model=RecommendationResponse)
async def get_home_recommendations(
    user_id: Optional[str] = None,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """
    Get home page recommendations for a user.
    
    Args:
        user_id: ID of the user to get recommendations for
        limit: Maximum number of recommendations to return
        db: Database session dependency
        
    Returns:
        List of recommended posts
    """
    try:
        # If no user_id provided, use a default
        if not user_id:
            user_id = "1"
        
        # Get candidate posts from recall service
        candidate_posts = recall_service.get_candidates(user_id, limit * 2)
        
        # Re-rank candidates using rank service
        ranked_posts = rank_service.rerank(user_id, candidate_posts)
        
        # Limit to requested number of posts
        final_posts = ranked_posts[:limit]
        
        return RecommendationResponse(posts=final_posts)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))