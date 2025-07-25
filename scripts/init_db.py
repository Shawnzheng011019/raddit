import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base, User, Post
from app.db.session import SessionLocal

def init_db():
    """Initialize the database with tables and sample data"""
    # Import all models to ensure they are registered
    from app.models import Base
    
    # Create all tables
    from app.db.session import engine
    Base.metadata.create_all(bind=engine)
    
    # Add sample data
    db = SessionLocal()
    
    try:
        # Check if we already have users
        if db.query(User).first() is None:
            # Create sample users
            users = [
                User(username="alice", email="alice@example.com"),
                User(username="bob", email="bob@example.com"),
                User(username="charlie", email="charlie@example.com"),
            ]
            
            for user in users:
                db.add(user)
            
            db.commit()
            
            # Get the users with their IDs
            db_users = db.query(User).all()
            
            # Create sample posts
            posts = [
                Post(title="Welcome to Raddit!", content="This is the first post on Raddit.", author_id=db_users[0].id),
                Post(title="How to use the recommendation system", content="The recommendation system uses a Two-Tower model for recall and Wide & Deep model for ranking.", author_id=db_users[1].id),
                Post(title="Tips for posting", content="Here are some tips for creating great posts on Raddit.", author_id=db_users[2].id),
            ]
            
            for post in posts:
                db.add(post)
            
            db.commit()
            print("Database initialized with sample data")
        else:
            print("Database already contains data")
    except Exception as e:
        print(f"Error initializing database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_db()