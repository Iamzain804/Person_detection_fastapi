from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    PROJECT_NAME: str = "Person Detection API"
    API_KEY: str = "your-super-secret-api-key"
    MODEL_PATH: str = "yolov8n.pt"  # Nano version for efficiency
    LOG_FILE: str = "logs/api.log"
    DEBUG: bool = True

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()
