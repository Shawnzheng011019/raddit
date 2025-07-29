from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Dict, Optional
import numpy as np
from app.models import User, Post, Interest, UserInterestWeight, UserBehaviorScore, user_interests
from app.services.recall_service import RecallService
from app.services.rank_service import RankService
import json

class InterestBasedRecommender:
    """
    Enhanced recommendation service that uses user interests for initial recommendations
    and refines based on user behavior over time.
    """
    
    def __init__(self):
        self.recall_service = RecallService()
        self.rank_service = RankService()
    
    def get_initial_recommendations(self, user_id: int, db: Session, limit: int = 20) -> List[Dict]:
        """
        Get initial recommendations for a new user based on their selected interests.
        """
        # Get user's interests
        user_interests = self._get_user_interests(user_id, db)
        
        if not user_interests:
            # Fallback to popular posts if no interests selected
            return self._get_popular_posts(db, limit)
        
        # Get posts matching user interests with initial weighting
        posts = self._get_interest_based_posts(user_id, user_interests, db, limit)
        
        return posts
    
    def get_personalized_recommendations(self, user_id: int, db: Session, limit: int = 20) -> List[Dict]:
        """
        Get personalized recommendations based on user behavior and interests.
        """
        # Get user's interests with weights
        user_interests = self._get_user_interests_with_weights(user_id, db)
        
        # Get behavior scores
        behavior_scores = self._get_user_behavior_scores(user_id, db)
        
        # Combine interest weights with behavior scores
        combined_scores = self._combine_interest_behavior_scores(user_interests, behavior_scores)
        
        # Get posts based on combined scores
        posts = self._get_personalized_posts(user_id, combined_scores, db, limit)
        
        return posts
    
    def _get_user_interests(self, user_id: int, db: Session) -> List[Dict]:
        """Get user's interests with categories"""
        interests = db.query(Interest).join(user_interests).filter(
            user_interests.c.user_id == user_id
        ).all()
        
        return [
            {
                'id': interest.id,
                'name': interest.name,
                'category': interest.category,
                'subcategory': interest.subcategory,
                'weight': 1.0  # Initial weight
            }
            for interest in interests
        ]
    
    def _get_user_interests_with_weights(self, user_id: int, db: Session) -> List[Dict]:
        """Get user's interests with learned weights"""
        query = db.query(
            Interest,
            UserInterestWeight.weight,
            UserInterestWeight.updated_at
        ).join(
            UserInterestWeight, Interest.id == UserInterestWeight.interest_id
        ).filter(
            UserInterestWeight.user_id == user_id
        ).order_by(
            desc(UserInterestWeight.weight)
        ).all()
        
        return [
            {
                'id': interest.id,
                'name': interest.name,
                'category': interest.category,
                'subcategory': interest.subcategory,
                'weight': weight,
                'updated_at': updated_at
            }
            for interest, weight, updated_at in query
        ]
    
    def _get_user_behavior_scores(self, user_id: int, db: Session) -> Dict[int, Dict]:
        """Get user's behavior scores for interests"""
        scores = db.query(UserBehaviorScore).filter(
            UserBehaviorScore.user_id == user_id
        ).all()
        
        return {
            score.interest_id: {
                'score': score.score,
                'interaction_count': score.interaction_count,
                'last_interaction': score.last_interaction
            }
            for score in scores
        }
    
    def _combine_interest_behavior_scores(self, interests: List[Dict], 
                                       behavior_scores: Dict[int, Dict]) -> Dict[int, float]:
        """Combine interest weights with behavior scores"""
        combined_scores = {}
        
        for interest in interests:
            interest_id = interest['id']
            base_weight = interest['weight']
            
            if interest_id in behavior_scores:
                behavior_score = behavior_scores[interest_id]['score']
                interaction_count = behavior_scores[interest_id]['interaction_count']
                
                # Combine base weight with behavior score
                # More recent interactions have higher weight
                recency_factor = min(1.0, interaction_count / 10.0)  # Normalize interaction count
                combined_score = base_weight * (1 + behavior_score * recency_factor)
            else:
                combined_score = base_weight
            
            combined_scores[interest_id] = combined_score
        
        return combined_scores
    
    def _get_interest_based_posts(self, user_id: int, interests: List[Dict], 
                                db: Session, limit: int) -> List[Dict]:
        """Get posts that match user's interests"""
        interest_ids = [interest['id'] for interest in interests]
        
        # Get posts that have primary or secondary interests matching user's interests
        posts = db.query(Post, Interest).join(
            Interest, Post.primary_interest_id == Interest.id
        ).filter(
            Post.primary_interest_id.in_(interest_ids),
            Post.is_deleted == False
        ).order_by(
            desc(Post.created_at)
        ).limit(limit * 2).all()  # Get more to allow for ranking
        
        # Format results
        formatted_posts = []
        for post, interest in posts:
            formatted_posts.append({
                'id': post.id,
                'title': post.title,
                'content': post.content[:200] + '...' if len(post.content) > 200 else post.content,
                'author': post.author.username,
                'created_at': post.created_at.isoformat(),
                'primary_interest': {
                    'id': interest.id,
                    'name': interest.name,
                    'category': interest.category
                },
                'relevance_score': 1.0  # Initial score
            })
        
        # If we don't have enough posts, add secondary interest matches
        if len(formatted_posts) < limit:
            secondary_posts = self._get_secondary_interest_posts(interest_ids, db, 
                                                               limit - len(formatted_posts))
            formatted_posts.extend(secondary_posts)
        
        return formatted_posts[:limit]
    
    def _get_secondary_interest_posts(self, interest_ids: List[int], db: Session, 
                                    limit: int) -> List[Dict]:
        """Get posts with secondary interests matching user's interests"""
        posts = db.query(Post, Interest).join(
            Interest, Post.primary_interest_id == Interest.id
        ).filter(
            Post.is_deleted == False
        ).order_by(
            desc(Post.created_at)
        ).limit(limit * 2).all()
        
        filtered_posts = []
        for post, interest in posts:
            # Check if any secondary interests match
            secondary_interests = []
            if post.secondary_interest_ids:
                try:
                    secondary_interests = json.loads(post.secondary_interest_ids)
                except json.JSONDecodeError:
                    secondary_interests = []
            
            # Check for overlap with user's interests
            overlap = set(interest_ids) & set(secondary_interests)
            if overlap:
                filtered_posts.append({
                    'id': post.id,
                    'title': post.title,
                    'content': post.content[:200] + '...' if len(post.content) > 200 else post.content,
                    'author': post.author.username,
                    'created_at': post.created_at.isoformat(),
                    'primary_interest': {
                        'id': interest.id,
                        'name': interest.name,
                        'category': interest.category
                    },
                    'relevance_score': len(overlap) / len(interest_ids)  # Score based on overlap
                })
        
        return filtered_posts[:limit]
    
    def _get_personalized_posts(self, user_id: int, combined_scores: Dict[int, float], 
                              db: Session, limit: int) -> List[Dict]:
        """Get personalized posts based on combined interest and behavior scores"""
        interest_ids = list(combined_scores.keys())
        
        # Get posts ordered by relevance score
        posts = db.query(Post, Interest).join(
            Interest, Post.primary_interest_id == Interest.id
        ).filter(
            Post.primary_interest_id.in_(interest_ids),
            Post.is_deleted == False
        ).order_by(
            desc(Post.created_at)
        ).limit(limit * 2).all()
        
        # Calculate relevance scores for each post
        scored_posts = []
        for post, interest in posts:
            interest_id = interest.id
            relevance_score = combined_scores.get(interest_id, 0.0)
            
            scored_posts.append({
                'id': post.id,
                'title': post.title,
                'content': post.content[:200] + '...' if len(post.content) > 200 else post.content,
                'author': post.author.username,
                'created_at': post.created_at.isoformat(),
                'primary_interest': {
                    'id': interest.id,
                    'name': interest.name,
                    'category': interest.category
                },
                'relevance_score': relevance_score
            })
        
        # Sort by relevance score and return top posts
        scored_posts.sort(key=lambda x: x['relevance_score'], reverse=True)
        return scored_posts[:limit]
    
    def _get_popular_posts(self, db: Session, limit: int) -> List[Dict]:
        """Get popular posts as fallback"""
        posts = db.query(Post, Interest).join(
            Interest, Post.primary_interest_id == Interest.id, isouter=True
        ).filter(
            Post.is_deleted == False
        ).order_by(
            desc(Post.created_at)
        ).limit(limit).all()
        
        return [
            {
                'id': post.id,
                'title': post.title,
                'content': post.content[:200] + '...' if len(post.content) > 200 else post.content,
                'author': post.author.username,
                'created_at': post.created_at.isoformat(),
                'primary_interest': {
                    'id': interest.id if interest else None,
                    'name': interest.name if interest else 'General',
                    'category': interest.category if interest else 'General'
                },
                'relevance_score': 0.5  # Default score for popular posts
            }
            for post, interest in posts
        ]
    
    def update_user_interest_weights(self, user_id: int, interest_id: int, 
                                   interaction_type: str, db: Session):
        """Update user interest weights based on interactions"""
        # Get current weight
        weight_entry = db.query(UserInterestWeight).filter(
            UserInterestWeight.user_id == user_id,
            UserInterestWeight.interest_id == interest_id
        ).first()
        
        if not weight_entry:
            weight_entry = UserInterestWeight(
                user_id=user_id,
                interest_id=interest_id,
                weight=1.0
            )
            db.add(weight_entry)
        
        # Update weight based on interaction type
        interaction_weights = {
            'view': 0.1,
            'click': 0.3,
            'upvote': 0.5,
            'downvote': -0.3,
            'save': 0.7,
            'comment': 0.8,
            'share': 1.0
        }
        
        weight_change = interaction_weights.get(interaction_type, 0.1)
        new_weight = max(0.1, min(5.0, weight_entry.weight + weight_change))
        weight_entry.weight = new_weight
        
        # Update behavior score
        behavior_score = db.query(UserBehaviorScore).filter(
            UserBehaviorScore.user_id == user_id,
            UserBehaviorScore.interest_id == interest_id
        ).first()
        
        if behavior_score:
            behavior_score.interaction_count += 1
            behavior_score.score = min(1.0, behavior_score.score + (weight_change * 0.1))
            behavior_score.last_interaction = func.now()
        
        db.commit()

# Create singleton instance
interest_recommender = InterestBasedRecommender()