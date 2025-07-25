from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.db.session import get_db
from sqlalchemy.orm import Session
from app.models import UserEvent

router = APIRouter()

class UserEventCreate(BaseModel):
    user_id: str
    event_type: str
    post_id: str

class UserEventResponse(BaseModel):
    id: int
    user_id: str
    event_type: str
    post_id: str
    timestamp: str

@router.post("/event", response_model=UserEventResponse)
async def record_user_event(
    event: UserEventCreate,
    db: Session = Depends(get_db)
):
    """
    Record a user event (click, view, upvote, etc.)
    
    Args:
        event: User event data
        db: Database session dependency
        
    Returns:
        Recorded event
    """
    try:
        db_event = UserEvent(
            user_id=event.user_id,
            event_type=event.event_type,
            post_id=event.post_id
        )
        db.add(db_event)
        db.commit()
        db.refresh(db_event)
        return UserEventResponse(
            id=db_event.id,
            user_id=db_event.user_id,
            event_type=db_event.event_type,
            post_id=db_event.post_id,
            timestamp=db_event.timestamp.isoformat()
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))