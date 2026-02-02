import logging
from app.core.database import SessionLocal
from app.services.vector_service import VectorService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_vector_service():
  session = SessionLocal()
  try:
    logger.info("=== Testing VectorService (Semantic Search) ===")
    
    service = VectorService()
    
    # UC1: Semantic Search
    query = "son màu đỏ dưỡng ẩm"
    logger.info(f"Test 1: Search similar products for query: '{query}'")
    
    results = service.search_similar_products(session, query_text=query, top_k=3)
    
    logger.info(f"Result: Found {len(results)} matches")
    for i, res in enumerate(results):
      logger.info(f"  {i+1}. {res['name']}")
      highlights = res.get('highlights') or ""
      logger.info(f"     Highlights: {highlights[:100]}...")

    # EC1: Nonsense Query
    query = "xe hơi chạy điện"
    logger.info(f"Test 2: Out of domain query: '{query}'")
    results = service.search_similar_products(session, query_text=query, top_k=3)
    logger.info(f"Result: Found {len(results)} matches (May still find something based on text overlap, but low relevance)")
    if results:
      logger.info(f"  Top match: {results[0]['name']}")

  except Exception as e:
    logger.error(f"Test Failed: {e}")
  finally:
    session.close()

if __name__ == "__main__":
  test_vector_service()
