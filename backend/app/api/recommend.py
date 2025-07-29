from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from app.services import recall_service, rank_service
from app.services.interest_based_recommender import interest_recommender
from app.db.session import get_db
from sqlalchemy.orm import Session

router = APIRouter()

# Pydantic models for request/response
class InterestResponse(BaseModel):
    id: int
    name: str
    category: str

class PostResponse(BaseModel):
    id: int
    title: str
    content: str
    author: str
    timestamp: str
    primary_interest: Optional[InterestResponse] = None
    relevance_score: Optional[float] = None

class RecommendationResponse(BaseModel):
    posts: List[PostResponse]
    user_id: int
    recommendation_type: str

@router.get("/home", response_model=RecommendationResponse)
async def get_home_recommendations(
    user_id: Optional[str] = None,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """
    Get home page recommendations for a user using interest-based and behavior-based system.
    
    Args:
        user_id: ID of the user to get recommendations for
        limit: Maximum number of recommendations to return
        db: Database session dependency
        
    Returns:
        List of recommended posts with interest information
    """
    try:
        # If no user_id provided, use a default
        if not user_id:
            user_id = "1"
        
        # Convert to int
        user_id_int = int(user_id)
        
        # Check if user has completed onboarding
        from app.models import User
        user = db.query(User).filter(User.id == user_id_int).first()
        
        if not user:
            # User doesn't exist, return popular posts
            posts = interest_recommender._get_popular_posts(db, limit)
            return RecommendationResponse(
                posts=posts,
                user_id=user_id_int,
                recommendation_type="popular"
            )
        
        if not user.has_completed_onboarding:
            # User hasn't completed onboarding, return popular posts
            posts = interest_recommender._get_popular_posts(db, limit)
            return RecommendationResponse(
                posts=posts,
                user_id=user_id_int,
                recommendation_type="popular"
            )
        
        # Get personalized recommendations
        posts = interest_recommender.get_personalized_recommendations(user_id_int, db, limit)
        
        return RecommendationResponse(
            posts=posts,
            user_id=user_id_int,
            recommendation_type="personalized"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/initial", response_model=RecommendationResponse)
async def get_initial_recommendations(
    user_id: int,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """
    Get initial recommendations for a user based on their selected interests.
    This is used for new users who just completed onboarding.
    
    Args:
        user_id: ID of the user
        limit: Maximum number of recommendations to return
        db: Database session dependency
        
    Returns:
        List of recommended posts based on initial interests
    """
    try:
        posts = interest_recommender.get_initial_recommendations(user_id, db, limit)
        
        return RecommendationResponse(
            posts=posts,
            user_id=user_id,
            recommendation_type="initial"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/popular", response_model=RecommendationResponse)
async def get_popular_recommendations(
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """
    Get popular posts as fallback recommendations.
    
    Args:
        limit: Maximum number of recommendations to return
        db: Database session dependency
        
    Returns:
        List of popular posts
    """
    try:
        posts = interest_recommender._get_popular_posts(db, limit)
        
        return RecommendationResponse(
            posts=posts,
            user_id=0,
            recommendation_type="popular"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))