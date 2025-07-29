from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey, Table
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime
from app.models import Base

# Association table for many-to-many relationship between users and interests
user_interests = Table(
    'user_interests',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('interest_id', Integer, ForeignKey('interests.id'), primary_key=True),
    Column('created_at', DateTime, default=datetime.utcnow)
)

class Interest(Base):
    __tablename__ = "interests"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    category = Column(String, index=True)  # Main category
    subcategory = Column(String, index=True)  # Subcategory
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship with users
    users = relationship("User", secondary=user_interests, back_populates="interests")

class UserInterestWeight(Base):
    __tablename__ = "user_interest_weights"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    interest_id = Column(Integer, ForeignKey("interests.id"))
    weight = Column(Integer, default=1)  # 1-5 scale based on user behavior
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="interest_weights")
    interest = relationship("Interest")