from app.core.config import settings
from app.core.database import SessionLocal
from app.services.embedding_service import EmbeddingService

def main():
  if not settings.GOOGLE_API_KEY:
    raise RuntimeError("GOOGLE_API_KEY missing in settings")

  service = EmbeddingService(api_key=settings.GOOGLE_API_KEY)
  session = SessionLocal()

  try:
    service.run(session)
    print("Embedding job finished")
  finally:
    session.close()

if __name__ == "__main__":
  main()
