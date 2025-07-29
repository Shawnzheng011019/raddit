from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.db.session import get_db
from sqlalchemy.orm import Session
from app.models import UserEvent, Post, Interest
from app.services.interest_based_recommender import interest_recommender
import json

router = APIRouter()

class UserEventCreate(BaseModel):
    user_id: str
    event_type: str
    post_id: str
    engagement_score: Optional[float] = 0.0

class UserEventResponse(BaseModel):
    id: int
    user_id: str
    event_type: str
    post_id: str
    engagement_score: float
    timestamp: str

@router.post("/event", response_model=UserEventResponse)
async def record_user_event(
    event: UserEventCreate,
    db: Session = Depends(get_db)
):
    """
    Record a user event (click, view, upvote, etc.) and update interest weights
    
    Args:
        event: User event data
        db: Database session dependency
        
    Returns:
        Recorded event
    """
    try:
        # Record the user event
        db_event = UserEvent(
            user_id=event.user_id,
            event_type=event.event_type,
            post_id=event.post_id,
            engagement_score=event.engagement_score
        )
        db.add(db_event)
        
        # Update user interest weights based on post's primary interest
        post = db.query(Post).filter(Post.id == int(event.post_id)).first()
        if post and post.primary_interest_id:
            interest_recommender.update_user_interest_weights(
                user_id=int(event.user_id),
                interest_id=post.primary_interest_id,
                interaction_type=event.event_type,
                db=db
            )
        
        # Also update weights for secondary interests if they exist
        if post and post.secondary_interest_ids:
            try:
                secondary_interests = json.loads(post.secondary_interest_ids)
                for interest_id in secondary_interests:
                    interest_recommender.update_user_interest_weights(
                        user_id=int(event.user_id),
                        interest_id=interest_id,
                        interaction_type=event.event_type,
                        db=db
                    )
            except json.JSONDecodeError:
                pass  # Ignore if secondary interests are not valid JSON
        
        db.commit()
        db.refresh(db_event)
        return UserEventResponse(
            id=db_event.id,
            user_id=db_event.user_id,
            event_type=db_event.event_type,
            post_id=db_event.post_id,
            engagement_score=db_event.engagement_score,
            timestamp=db_event.timestamp.isoformat()
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))