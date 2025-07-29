from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey, Table, Float
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()

# Association table for many-to-many relationship between users and interests
user_interests = Table(
    'user_interests',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('interest_id', Integer, ForeignKey('interests.id'), primary_key=True),
    Column('created_at', DateTime, default=datetime.utcnow),
    Column('initial_weight', Float, default=1.0)
)

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    has_completed_onboarding = Column(Boolean, default=False)
    
    # Relationship with posts
    posts = relationship("Post", back_populates="author")
    # Relationship with user events
    events = relationship("UserEvent", back_populates="user")
    # Relationship with interests
    interests = relationship("Interest", secondary=user_interests, back_populates="users")
    # Relationship with interest weights
    interest_weights = relationship("UserInterestWeight", back_populates="user")
    # Relationship with user behavior tracking
    behavior_scores = relationship("UserBehaviorScore", back_populates="user")

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

class Post(Base):
    __tablename__ = "posts"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    content = Column(Text)
    author_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    is_deleted = Column(Boolean, default=False)
    
    # Relationship with users
    author = relationship("User", back_populates="posts")
    # Relationship with user events
    events = relationship("UserEvent", back_populates="post")

class UserInterestWeight(Base):
    __tablename__ = "user_interest_weights"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    interest_id = Column(Integer, ForeignKey("interests.id"))
    weight = Column(Float, default=1.0)  # 0.0-5.0 scale based on user behavior
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="interest_weights")
    interest = relationship("Interest")

class UserBehaviorScore(Base):
    __tablename__ = "user_behavior_scores"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    interest_id = Column(Integer, ForeignKey("interests.id"))
    score = Column(Float, default=0.0)  # Calculated score based on user interactions
    interaction_count = Column(Integer, default=0)  # Number of interactions with this interest
    last_interaction = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="behavior_scores")
    interest = relationship("Interest")

class Post(Base):
    __tablename__ = "posts"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    content = Column(Text)
    author_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    is_deleted = Column(Boolean, default=False)
    
    # Content classification fields
    primary_interest_id = Column(Integer, ForeignKey("interests.id"))
    secondary_interest_ids = Column(String)  # JSON array of interest IDs
    content_tags = Column(String)  # JSON array of tags
    
    # Relationship with users
    author = relationship("User", back_populates="posts")
    # Relationship with user events
    events = relationship("UserEvent", back_populates="post")
    # Relationship with interests
    primary_interest = relationship("Interest")

class UserEvent(Base):
    __tablename__ = "user_events"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    post_id = Column(Integer, ForeignKey("posts.id"))
    event_type = Column(String)  # click, view, upvote, downvote, save, comment, share
    engagement_score = Column(Float, default=0.0)  # 0.0-1.0 based on engagement depth
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationship with users and posts
    user = relationship("User", back_populates="events")
    post = relationship("Post", back_populates="events")