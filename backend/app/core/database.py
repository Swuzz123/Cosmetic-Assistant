from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Create Async Engine
# echo=True will log SQL queries to console (useful for debugging)
engine = create_async_engine(settings.DATABASE_URL, echo=True)

# Create Session Factory
AsyncSessionLocal = sessionmaker(
  bind=engine,
  class_=AsyncSession,
  expire_on_commit=False,
  autocommit=False,
  autoflush=False,
)

async def get_db():
  """
  Dependency generator for FastAPI routes to get a DB session.
  """
  async with AsyncSessionLocal() as session:
    try:
      yield session
    finally:
      await session.close()
