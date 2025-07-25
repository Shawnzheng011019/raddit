import numpy as np
from pymilvus import (
    connections,
    FieldSchema, CollectionSchema, DataType,
    Collection, utility
)
import sys
import os

# Add wide-deep directory to path to import models
sys.path.append(os.path.join(os.path.dirname(__file__), "../wide-deep/src"))

from recall.two_tower import TwoTowerModel
import torch

def create_milvus_collection():
    """Create Milvus collection for storing item embeddings"""
    try:
        # Connect to Milvus
        connections.connect(alias="default", host="localhost", port="19530")
        
        # Drop collection if it exists
        if utility.has_collection("item_embeddings"):
            utility.drop_collection("item_embeddings")
        
        # Create collection schema
        fields = [
            FieldSchema(name="post_id", dtype=DataType.INT64, is_primary=True, auto_id=False),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=64)
        ]
        
        schema = CollectionSchema(fields=fields, description="Post embeddings")
        collection = Collection(name="item_embeddings", schema=schema)
        
        # Create index
        index_params = {
            "metric_type": "IP",
            "index_type": "IVF_FLAT",
            "params": {"nlist": 128}
        }
        
        collection.create_index(field_name="embedding", index_params=index_params)
        print("Created Milvus collection with index")
        return collection
    except Exception as e:
        print(f"Error creating Milvus collection: {e}")
        return None

def generate_sample_embeddings(collection):
    """Generate sample embeddings and insert into Milvus"""
    try:
        # Generate sample post embeddings
        post_ids = list(range(1, 101))  # 100 sample posts
        embeddings = []
        
        # Initialize a simple Two-Tower model for generating embeddings
        config = {
            'recall': {
                'embedding_dim': 64,
                'user_tower_hidden_dims': [128, 64],
                'item_tower_hidden_dims': [128, 64],
                'dropout': 0.2
            }
        }
        
        model = TwoTowerModel(config)
        
        # Generate embeddings for sample posts
        for post_id in post_ids:
            # Create mock item features
            item_features = {
                'post_id': torch.tensor([post_id]),
                'category': torch.tensor([post_id % 10]),  # Mock category
                'author_id': torch.tensor([post_id % 50]),  # Mock author
            }
            
            # Get item embedding
            with torch.no_grad():
                embedding = model.forward_item_tower(item_features)
                embeddings.append(embedding.numpy().flatten())
        
        # Insert into Milvus
        if collection:
            entities = [post_ids, embeddings]
            collection.insert(entities)
            collection.flush()
            print(f"Inserted {len(post_ids)} sample embeddings into Milvus")
        else:
            print("Collection not available")
    except Exception as e:
        print(f"Error generating embeddings: {e}")

def main():
    """Main function to set up Milvus"""
    collection = create_milvus_collection()
    generate_sample_embeddings(collection)

if __name__ == "__main__":
    main()