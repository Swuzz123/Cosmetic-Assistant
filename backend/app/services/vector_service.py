from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models import Product
from app.services.embedding_service import EmbeddingService
from app.core.config import settings

class VectorService:
  def __init__(self):
    self.embedding_service = EmbeddingService()

  def search_similar_products(
    self, 
    db: Session, 
    query_text: str, 
    top_k: int = 5
  ) -> List[Dict[str, Any]]:
    """
    Semantic search using pgvector (cosine similarity).
    """
    # 1. Generate embedding for query
    query_vector = self.embedding_service.embed_query(query_text)
    if not query_vector:
      return []

    # 2. Perform vector search in DB
    stmt = select(Product).order_by(Product.embedding.cosine_distance(query_vector)).limit(top_k)
    
    products = db.execute(stmt).scalars().all()

    # 3. Format results
    results = []
    for p in products:
      results.append({
        "product_id": p.product_id,
        "name": p.product_name,
        "description": p.description,
        "highlights": p.highlights,
      })
        
    return results
