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
  
  @property
  def DATABASE_URL(self) -> str:
    # TODO: This constructs the connection string. Ensure drivers (asyncpg) are installed.
    return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

  class Config:
    env_file = ".env"
    case_sensitive = True

settings = Settings()
