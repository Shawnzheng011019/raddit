from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship with posts
    posts = relationship("Post", back_populates="author")
    # Relationship with user events
    events = relationship("UserEvent", back_populates="user")

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

class UserEvent(Base):
    __tablename__ = "user_events"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    post_id = Column(Integer, ForeignKey("posts.id"))
    event_type = Column(String)  # click, view, upvote, etc.
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationship with users and posts
    user = relationship("User", back_populates="events")
    post = relationship("Post", back_populates="events")