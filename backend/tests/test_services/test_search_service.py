import logging
from app.core.database import SessionLocal
from app.services.search_service import SearchService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_search_service():
  session = SessionLocal()
  try:
    logger.info("=== Testing SearchService ===")

    # UC1: Basic Search (Brand)
    logger.info("Test 1: Search by Brand (e.g., 'Mac')")
    results = SearchService.search_products(session, brand_name="Mac")
    logger.info(f"Result: Found {len(results)} items")
    if results:
      logger.info(f"Sample: {results[0]['product_name']} ({results[0]['brand']})")

    # UC2: Price Range
    logger.info("Test 2: Search by Price (10 - 50)")
    results = SearchService.search_products(session, price_min=10, price_max=50)
    logger.info(f"Result: Found {len(results)} items")

    # UC3: Color Search
    logger.info("Test 3: Search by Color (e.g., 'Red')")
    results = SearchService.search_products(session, color="Red")
    logger.info(f"Result: Found {len(results)} items")
    if results:
      logger.info(f"Sample Color: {results[0]['color']}")

    # EC1: No Results
    logger.info("Test 4: Impossible Criteria (Edge Case)")
    results = SearchService.search_products(session, brand_name="NON_EXISTENT_BRAND_XYZ")
    logger.info(f"Result: Found {len(results)} items (Expected 0)")

  except Exception as e:
    logger.error(f"Test Failed: {e}")
  finally:
    session.close()

if __name__ == "__main__":
  test_search_service()
