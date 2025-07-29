from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select
from passlib.context import CryptContext
from app.db.session import get_db
from app.models import User, Interest, user_interests, UserInterestWeight, UserBehaviorScore
from app.data.interests_data import get_all_interests
import uuid
import json

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    interests: List[int]  # List of interest IDs

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    has_completed_onboarding: bool
    created_at: str

class InterestResponse(BaseModel):
    id: int
    name: str
    category: str
    subcategory: str
    description: Optional[str]

class InterestCategoryResponse(BaseModel):
    category: str
    subcategories: dict

class OnboardingCompleteRequest(BaseModel):
    user_id: int
    selected_interests: List[int]

@router.get("/interests", response_model=List[InterestResponse])
async def get_interests(db: Session = Depends(get_db)):
    """Get all available interests for user onboarding"""
    interests = db.query(Interest).all()
    return [InterestResponse(
        id=interest.id,
        name=interest.name,
        category=interest.category,
        subcategory=interest.subcategory,
        description=interest.description
    ) for interest in interests]

@router.get("/interests/categories", response_model=List[InterestCategoryResponse])
async def get_interests_by_category(db: Session = Depends(get_db)):
    """Get all interests organized by category and subcategory"""
    from app.data.interests_data import get_interests_by_category
    categories_data = get_interests_by_category()
    
    response = []
    for category, data in categories_data.items():
        response.append(InterestCategoryResponse(
            category=category,
            subcategories=data["subcategories"]
        ))
    return response

@router.post("/register", response_model=UserResponse)
async def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user with selected interests"""
    
    # Check if username already exists
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Check if email already exists
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Validate interests
    if not user.interests:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one interest must be selected"
        )
    
    # Check if all interests exist
    interest_ids = set(user.interests)
    existing_interests = db.query(Interest).filter(Interest.id.in_(interest_ids)).all()
    existing_ids = {interest.id for interest in existing_interests}
    
    if len(existing_ids) != len(interest_ids):
        missing_ids = interest_ids - existing_ids
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid interest IDs: {missing_ids}"
        )
    
    # Hash password
    hashed_password = pwd_context.hash(user.password)
    
    # Create user
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        has_completed_onboarding=True
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Add user interests with initial weights
    for interest_id in user.interests:
        # Add to user_interests table
        stmt = user_interests.insert().values(
            user_id=db_user.id,
            interest_id=interest_id,
            initial_weight=1.0
        )
        db.execute(stmt)
        
        # Add to user_interest_weights table for behavior tracking
        interest_weight = UserInterestWeight(
            user_id=db_user.id,
            interest_id=interest_id,
            weight=1.0
        )
        db.add(interest_weight)
        
        # Initialize behavior score
        behavior_score = UserBehaviorScore(
            user_id=db_user.id,
            interest_id=interest_id,
            score=0.0,
            interaction_count=0
        )
        db.add(behavior_score)
    
    db.commit()
    
    return UserResponse(
        id=db_user.id,
        username=db_user.username,
        email=db_user.email,
        has_completed_onboarding=db_user.has_completed_onboarding,
        created_at=db_user.created_at.isoformat()
    )

@router.post("/onboarding/complete")
async def complete_onboarding(request: OnboardingCompleteRequest, db: Session = Depends(get_db)):
    """Complete user onboarding with selected interests"""
    
    user = db.query(User).filter(User.id == request.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if not request.selected_interests:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one interest must be selected"
        )
    
    # Clear existing interests
    db.execute(user_interests.delete().where(user_interests.c.user_id == user.id))
    db.query(UserInterestWeight).filter(UserInterestWeight.user_id == user.id).delete()
    db.query(UserBehaviorScore).filter(UserBehaviorScore.user_id == user.id).delete()
    
    # Add new interests
    for interest_id in request.selected_interests:
        # Add to user_interests table
        stmt = user_interests.insert().values(
            user_id=user.id,
            interest_id=interest_id,
            initial_weight=1.0
        )
        db.execute(stmt)
        
        # Add to user_interest_weights table
        interest_weight = UserInterestWeight(
            user_id=user.id,
            interest_id=interest_id,
            weight=1.0
        )
        db.add(interest_weight)
        
        # Initialize behavior score
        behavior_score = UserBehaviorScore(
            user_id=user.id,
            interest_id=interest_id,
            score=0.0,
            interaction_count=0
        )
        db.add(behavior_score)
    
    user.has_completed_onboarding = True
    db.commit()
    
    return {"message": "Onboarding completed successfully"}

@router.get("/user/{user_id}/interests", response_model=List[InterestResponse])
async def get_user_interests(user_id: int, db: Session = Depends(get_db)):
    """Get interests for a specific user"""
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    interests = db.query(Interest).join(user_interests).filter(user_interests.c.user_id == user_id).all()
    
    return [InterestResponse(
        id=interest.id,
        name=interest.name,
        category=interest.category,
        subcategory=interest.subcategory,
        description=interest.description
    ) for interest in interests]

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Generate password hash"""
    return pwd_context.hash(password)