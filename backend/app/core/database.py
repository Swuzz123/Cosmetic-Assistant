from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker as sessionmaker_sync

from app.core.config import settings

# -------------------------------- ASYNC ENGINE --------------------------------
engine_async = create_async_engine(settings.DATABASE_URL_ASYNC, echo=False)
AsyncSessionLocal = sessionmaker(
  bind=engine_async,
  class_=AsyncSession,
  expire_on_commit=False,
  autocommit=False,
  autoflush=False,
)

async def get_async_db():
  """Dependency cho FastAPI"""
  async with AsyncSessionLocal() as session:
    try:
      yield session
    finally:
      await session.close()

# -------------------------------- SYNC ENGINE ---------------------------------
engine_sync = create_engine(settings.DATABASE_URL_SYNC, echo=False)
SessionLocal = sessionmaker_sync(
  autocommit=False, 
  autoflush=False, 
  bind=engine_sync
)

def get_sync_db():
  """Context Manager for running script background"""
  db = SessionLocal()
  try:
    yield db
  finally:
    db.close()