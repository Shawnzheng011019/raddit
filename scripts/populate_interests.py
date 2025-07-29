import os
import sys
from sqlalchemy.orm import sessionmaker
from app.db.session import SessionLocal, engine
from app.models import Base, Interest
from app.data.interests_data import get_all_interests

def populate_interests():
    """Populate the database with all interest categories"""
    db = SessionLocal()
    
    try:
        # Get all interests as flat list
        interests_data = get_all_interests()
        
        # Check if interests already exist
        existing_interests = db.query(Interest).count()
        if existing_interests > 0:
            print(f"Database already contains {existing_interests} interests")
            return
        
        # Create interests
        created_count = 0
        for interest_data in interests_data:
            # Check if interest already exists
            existing = db.query(Interest).filter(
                Interest.name == interest_data["name"]
            ).first()
            
            if not existing:
                interest = Interest(
                    name=interest_data["name"],
                    category=interest_data["category"],
                    subcategory=interest_data["subcategory"],
                    description=f"{interest_data['category']} - {interest_data['subcategory']}: {interest_data['name']}"
                )
                db.add(interest)
                created_count += 1
        
        db.commit()
        print(f"Successfully populated {created_count} interests")
        
        # Print summary
        categories = {}
        interests = db.query(Interest).all()
        for interest in interests:
            if interest.category not in categories:
                categories[interest.category] = {}
            if interest.subcategory not in categories[interest.category]:
                categories[interest.category][interest.subcategory] = 0
            categories[interest.category][interest.subcategory] += 1
        
        print("\nInterest Categories Summary:")
        for category, subcategories in categories.items():
            print(f"\n{category}:")
            for subcategory, count in subcategories.items():
                print(f"  {subcategory}: {count} interests")
                
    except Exception as e:
        db.rollback()
        print(f"Error populating interests: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    # Add the backend directory to the path
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))
    populate_interests()