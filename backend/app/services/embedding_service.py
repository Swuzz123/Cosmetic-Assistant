import time
from typing import List
from sqlalchemy import select
from sqlalchemy.orm import Session
from google import genai
from google.genai import types

from app.models import Product
from app.core.logging import setup_logging

logger = setup_logging()

class EmbeddingService:
  def __init__(
    self,
    model_name: str = "text-embedding-004",
    batch_size: int = 30,
    rpm_limit: int = 55,
    rpd_limit: int = 1450,
  ):
    from app.core.config import settings
    from app.utils.google_api_helper import KeyManager
    
    self.key_manager = KeyManager(settings)
    self.client = self._get_client()
    self.model_name = model_name
    self.batch_size = batch_size
    self.rpm_limit = rpm_limit
    self.rpd_limit = rpd_limit

  def _get_client(self):
    key = self.key_manager.get_current_key()
    return genai.Client(api_key=key)

  def _rotate_client(self):
    new_key = self.key_manager.rotate_key()
    self.client = genai.Client(api_key=new_key)

  # ----------------------------------------------------------------------------
  def _embed_content_with_retry(
    self, 
    texts: List[str], 
    task_type: str
  ) -> List[List[float]]:
    from app.utils.google_api_helper import GoogleAPIChecker
    
    for attempt in range(5): 
      try:
        res = self.client.models.embed_content(
          model=self.model_name,
          contents=texts,
          config=types.EmbedContentConfig(
            task_type=task_type
          ),
        )
        return [e.values for e in res.embeddings]
      
      except Exception as e:
        status = GoogleAPIChecker.extract_status_code(e)
        logger.warning(f"Embedding error: {e} (Status: {status})")
        
        # Check if we should rotate key
        if status and GoogleAPIChecker.should_rotate_key(status):
          logger.warning("Quota/Permission issue detected. Rotating API key...")
          self._rotate_client()
          # Don't sleep long if we rotated, just retry immediately or short pause
          time.sleep(1)
          continue
            
        wait = 2 ** (attempt + 1)
        logger.warning(f"Retry in {wait}s")
        time.sleep(wait)

    logger.error("Failed to embed content after all retries.")
    return []

  # ----------------------------------------------------------------------------
  def embed_documents(self, texts: List[str]) -> List[List[float]]:
    """Public method for embedding database documents"""
    return self._embed_content_with_retry(texts, "RETRIEVAL_DOCUMENT")

  # ----------------------------------------------------------------------------
  def embed_query(self, text: str) -> List[float]:
    """Public method for embedding a search query. Returns single vector."""
    vectors = self._embed_content_with_retry([text], "RETRIEVAL_QUERY")
    return vectors[0] if vectors else []

  # ----------------------------------------------------------------------------
  def _embed_with_retry(self, texts: List[str]) -> List[List[float]]:
    return self.embed_documents(texts)

  # ----------------------------------------------------------------------------
  def prepare_text(self, product: Product) -> str:
    return (
      f"Product: {product.product_name}. "
      f"Desc: {product.description or ''}. "
      f"Highlights: {product.highlights or ''}. "
      f"Ingredients: {product.ingredients or ''}."
    ).replace("\n", " ").strip()

  # ----------------------------------------------------------------------------
  def run(self, session: Session):
    products = session.execute(
      select(Product).filter(Product.embedding == None)
    ).scalars().all()

    logger.info(f"Found {len(products)} products to embed")

    min_count = 0
    daily_count = 0
    start_time = time.time()

    for i in range(0, len(products), self.batch_size):
      if daily_count >= self.rpd_limit:
        logger.error("Daily limit reached")
        break

      if min_count >= self.rpm_limit:
        elapsed = time.time() - start_time
        if elapsed < 60:
          time.sleep(60 - elapsed + 1)
        min_count = 0
        start_time = time.time()

      batch = products[i : i + self.batch_size]
      texts = [self.prepare_text(p) for p in batch]

      vectors = self._embed_with_retry(texts)
      min_count += 1
      daily_count += 1

      if len(vectors) != len(batch):
        logger.error("Vector mismatch, skipping batch")
        continue

      for p, v in zip(batch, vectors):
        p.embedding = v

      session.commit()
      time.sleep(0.2)
