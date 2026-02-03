from app.core.config import settings
from app.core.database import SessionLocal
from app.services.embedding_service import EmbeddingService

def main():
  if not settings.GOOGLE_API_KEYS:
    raise RuntimeError("GOOGLE_API_KEY missing in settings")

  all_keys = [k.strip() for k in settings.GOOGLE_API_KEYS.split(',') if k.strip()]
  if not all_keys:
    raise RuntimeError("No keys found in GOOGLE_API_KEYS")

  # Use all available keys to allow rotation if one fails (e.g. leaked or quota exceeded)
  print(f"Running embedding with {len(all_keys)} keys to support rotation...")

  service = EmbeddingService(api_keys=all_keys)
  session = SessionLocal()

  try:
    service.run(session)
    print("Embedding job finished")
  finally:
    session.close()

if __name__ == "__main__":
  main()
