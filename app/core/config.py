from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    PROJECT_NAME: str = "Person Detection API"
    API_KEY: str = "your-super-secret-api-key"
    MODEL_PATH: str = "yolov8n.pt"  # Nano version for efficiency
    LOG_FILE: str = "logs/api.log"
    DEBUG: bool = True

    # Database Settings
    DATABASE_TYPE: str = "sqlite" # Default to sqlite
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "password"
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: str = "5432"
    POSTGRES_DB: str = "person_detection"

    @property
    def DATABASE_URL(self) -> str:
        if self.DATABASE_TYPE == "postgresql":
            return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        return "sqlite:///./sql_app.db"

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()
