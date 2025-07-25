import torch
import numpy as np
from pymilvus import connections, Collection
from app.core.config import settings
from app.core.logger import logger
import sys
import os

# Add wide-deep directory to path to import models
sys.path.append(os.path.join(os.path.dirname(__file__), "../../wide-deep/src"))

from recall.two_tower import TwoTowerModel

class RecallService:
    def __init__(self):
        self.milvus_collection = None
        self.two_tower_model = None
        self._init_milvus()
        self._load_model()
    
    def _init_milvus(self):
        """Initialize connection to Milvus"""
        try:
            connections.connect(
                alias="default",
                host=settings.milvus_host,
                port=settings.milvus_port
            )
            self.milvus_collection = Collection(settings.milvus_collection_name)
            self.milvus_collection.load()
            logger.info("Connected to Milvus and loaded collection")
        except Exception as e:
            logger.error(f"Failed to connect to Milvus: {e}")
    
    def _load_model(self):
        """Load the Two-Tower model"""
        try:
            # Initialize model with config (using default values for now)
            config = {
                'recall': {
                    'embedding_dim': 64,
                    'user_tower_hidden_dims': [128, 64],
                    'item_tower_hidden_dims': [128, 64],
                    'dropout': 0.2
                }
            }
            
            self.two_tower_model = TwoTowerModel(config)
            
            # Load model weights if they exist
            if os.path.exists(settings.two_tower_model_path):
                self.two_tower_model.load_state_dict(torch.load(settings.two_tower_model_path))
                logger.info("Loaded Two-Tower model")
            else:
                logger.warning("Two-Tower model file not found, using initialized model")
        except Exception as e:
            logger.error(f"Failed to load Two-Tower model: {e}")
    
    def get_user_embedding(self, user_id: str) -> np.ndarray:
        """Generate user embedding using the Two-Tower model"""
        try:
            # In a real implementation, we would fetch user features from database
            # For demo purposes, we'll create mock features
            user_features = {
                'user_id': torch.tensor([int(user_id)]),
                'age': torch.tensor([25]),  # Mock age
                'gender': torch.tensor([1]),  # Mock gender (1=male, 0=female)
                'interests': torch.tensor([5])  # Mock interests category
            }
            
            # Get user embedding
            with torch.no_grad():
                user_embedding = self.two_tower_model.forward_user_tower(user_features)
                return user_embedding.numpy().flatten()
        except Exception as e:
            logger.error(f"Failed to generate user embedding: {e}")
            # Return a random embedding as fallback
            return np.random.rand(64)
    
    def get_candidates(self, user_id: str, limit: int = 20) -> list:
        """Get candidate posts using Milvus vector search"""
        try:
            # Get user embedding
            user_embedding = self.get_user_embedding(user_id)
            
            # Search in Milvus
            if self.milvus_collection:
                search_params = {
                    "metric_type": "IP",
                    "params": {"nprobe": 10},
                }
                
                results = self.milvus_collection.search(
                    data=[user_embedding.tolist()],
                    anns_field="embedding",
                    param=search_params,
                    limit=limit,
                    expr=None,
                    output_fields=["post_id"],
                    consistency_level="Strong"
                )
                
                # Extract post IDs from results
                post_ids = []
                for result in results[0]:
                    post_ids.append(result.entity.get("post_id"))
                
                return post_ids
            else:
                # Fallback: return random post IDs
                logger.warning("Milvus not available, returning mock post IDs")
                return list(range(1, min(limit + 1, 101)))  # Return IDs 1-20 or less
        except Exception as e:
            logger.error(f"Failed to get candidates from Milvus: {e}")
            # Fallback: return random post IDs
            return list(range(1, min(limit + 1, 101)))

# Create a singleton instance
recall_service = RecallService()