import os
from pydantic import BaseSettings

class Settings(BaseSettings):
    # Database settings
    database_url: str = "sqlite:///./raddit.db"
    
    # Milvus settings
    milvus_host: str = "localhost"
    milvus_port: str = "19530"
    milvus_collection_name: str = "item_embeddings"
    
    # Model paths
    wide_deep_model_path: str = "../wide-deep/models/wide_deep_model.pth"
    two_tower_model_path: str = "../wide-deep/models/two_tower_model.pth"
    
    class Config:
        env_file = ".env"

settings = Settings()