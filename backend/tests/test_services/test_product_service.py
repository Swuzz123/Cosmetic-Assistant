import logging
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.services.product_service import ProductService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_product_service():
  session = SessionLocal()
  try:
    logger.info("=== Testing ProductService ===")
    
    # UC1: Get Top Products
    logger.info("Test 1: Get Top 5 Products")
    products = ProductService.get_top_products(session, limit=5)
    logger.info(f"Result: Found {len(products)} products")
    if products:
      logger.info(f"Sample: {products[0].product_name}")
      # Save an ID for next test
      test_id = products[0].product_id
      
      # UC2: Get Product By ID
      logger.info(f"Test 2: Get Product By ID ({test_id})")
      product = ProductService.get_product_by_id(session, test_id)
      if product:
        logger.info(f"Result: {product.product_name} - Variants: {len(product.variants)}")
      else:
        logger.error("Result: Product not found (Unexpected)")

      # UC3: Get Variant
      if product.variants:
        variant_id = product.variants[0].uniq_id
        logger.info(f"Test 3: Get Variant details ({variant_id})")
        variant = ProductService.get_variant_inventory(session, variant_id)
        logger.info(f"Result: {variant.color} - Price: {variant.price}")
    
    # EC1: Non-existent product
    logger.info("Test 4: Get Non-existent Product (Edge Case)")
    missing = ProductService.get_product_by_id(session, "NON_EXISTENT_ID_999")
    logger.info(f"Result: {missing} (Expected None)")

  except Exception as e:
    logger.error(f"Test Failed: {e}")
  finally:
    session.close()

if __name__ == "__main__":
  test_product_service()
