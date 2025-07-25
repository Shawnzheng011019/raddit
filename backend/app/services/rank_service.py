import torch
import numpy as np
from app.core.config import settings
from app.core.logger import logger
import sys
import os

# Add wide-deep directory to path to import models
sys.path.append(os.path.join(os.path.dirname(__file__), "../../wide-deep/src"))

from model.wide_deep import WideAndDeep

class RankService:
    def __init__(self):
        self.wide_deep_model = None
        self._load_model()
    
    def _load_model(self):
        """Load the Wide & Deep model"""
        try:
            # Initialize model with config (using default values for now)
            config = {
                'model': {
                    'wide_dim': 1000,
                    'embedding_dim': 8,
                    'hidden_dims': [64, 32, 16],
                    'dropout': 0.2
                }
            }
            
            self.wide_deep_model = WideAndDeep(config)
            
            # Load model weights if they exist
            if os.path.exists(settings.wide_deep_model_path):
                self.wide_deep_model.load_state_dict(torch.load(settings.wide_deep_model_path))
                logger.info("Loaded Wide & Deep model")
            else:
                logger.warning("Wide & Deep model file not found, using initialized model")
        except Exception as e:
            logger.error(f"Failed to load Wide & Deep model: {e}")
    
    def rerank(self, user_id: str, post_ids: list) -> list:
        """Re-rank posts using the Wide & Deep model"""
        try:
            # In a real implementation, we would fetch features for each post
            # For demo purposes, we'll create mock features and randomly shuffle
            
            if self.wide_deep_model:
                # Create mock features for each post
                reranked_posts = []
                for post_id in post_ids:
                    # Create mock features
                    wide_features = torch.randn(1, 1000)  # Mock wide features
                    deep_features = {
                        'user_id': torch.tensor([[int(user_id)]]),
                        'post_id': torch.tensor([[int(post_id)]]),
                        'category': torch.tensor([[1]]),  # Mock category
                        'author': torch.tensor([[123]])   # Mock author ID
                    }
                    
                    # Get prediction score
                    with torch.no_grad():
                        score = self.wide_deep_model(wide_features, deep_features)
                        reranked_posts.append((post_id, score.item()))
                
                # Sort by score (descending)
                reranked_posts.sort(key=lambda x: x[1], reverse=True)
                return [post_id for post_id, score in reranked_posts]
            else:
                # Fallback: randomly shuffle posts
                logger.warning("Wide & Deep model not available, randomly shuffling posts")
                import random
                random.shuffle(post_ids)
                return post_ids
        except Exception as e:
            logger.error(f"Failed to re-rank posts: {e}")
            # Fallback: return original order
            return post_ids

# Create a singleton instance
rank_service = RankService()