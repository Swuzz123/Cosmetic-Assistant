from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
  # API Configuration
  API_V1_STR: str = "/api/v1"
  PROJECT_NAME: str = "Cosmetics Chatbot Assistant"
  
  # Database Configuration
  # TODO: These values should slightly match your docker-compose environment variables
  POSTGRES_USER: str = "postgres"
  POSTGRES_PASSWORD: str = "password"
  POSTGRES_SERVER: str = "localhost"
  POSTGRES_PORT: str = "5432"
  POSTGRES_DB: str = "cosmetics_db"

  # AI Service Configuration
  # TODO: Add your OpenAI or Gemini API Key here
  OPENAI_API_KEY: Optional[str] = None
  OPENAI_BASE_URL: Optional[str] = "https://integrate.api.nvidia.com/v1"
  MODEL_NAME: str = "meta/llama-3.3-70b-instruct"

  @property
  def SYNC_DATABASE_URL(self) -> str:
    # Synchronous connection string for Agent Tools (using psycopg2)
    return f"postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

  class Config:
    env_file = ".env"
    case_sensitive = True
    extra = "ignore"

settings = Settings()
