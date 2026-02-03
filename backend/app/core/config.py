from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
  # API Configuration
  API_V1_STR: str = "/api/v1"
  PROJECT_NAME: str = "Cosmetics Chatbot Assistant"
  
  # -------------------------- DATABASE CONFIGURATION --------------------------
  POSTGRES_USER: str = "admin"
  POSTGRES_PASSWORD: str = "admin"
  POSTGRES_SERVER: str = "localhost"
  POSTGRES_PORT: str = "5432"
  POSTGRES_DB: str = "cosmetics_db"

  # ------------------------- AI SERVICE CONFIGURATION -------------------------
  GOOGLE_API_KEYS: Optional[str] = None

  # Nvidia NIM (For Agent / LLM)
  NVIDIA_API_KEY: str
  NVIDIA_BASE_URL: str = "https://integrate.api.nvidia.com/v1"
  MODEL_NAME: str = "meta/llama-3.3-70b-instruct"

  # ------------------------------- DATABASE URLs ------------------------------
  @property
  def DATABASE_URL_SYNC(self) -> str:
    """Used for Scripts (such as embedding creation scripts) and Agent Tools (Sync)"""
    return f"postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

  @property
  def DATABASE_URL_ASYNC(self) -> str:
    """Used for FastAPI (Async) for higher performance"""
    return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

  class Config:
    env_file = ".env"
    case_sensitive = True
    extra = "ignore"

settings = Settings()