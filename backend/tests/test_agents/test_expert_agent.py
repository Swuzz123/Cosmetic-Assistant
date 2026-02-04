import logging
import sys
import os
from sqlalchemy import text

# Add the backend directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from app.ai.agents.expert_agent import ExpertAgent
from app.core.database import SessionLocal

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("TestExpertAgent")

def get_a_real_product_id():
  """Helper to get a valid product ID from DB for testing"""
  session = SessionLocal()
  try:
    # Get a product that has variants to full test
    result = session.execute(text("SELECT product_id FROM products LIMIT 1")).scalar()
    return result
  except Exception as e:
    logger.error(f"Failed to fetch product ID: {e}")
    return None
  finally:
    session.close()

def test_expert_agent():
  logger.info("=== Testing ExpertAgent ===")
  
  product_id = get_a_real_product_id()
  if not product_id:
    logger.error("No product found in DB to test with. Aborting.")
    return

  logger.info(f"Using Test Product ID: {product_id}")
  
  agent = ExpertAgent()

  try:
    # === Use Case 1: Ingredients/Safety ===
    logger.info("\n[Use Case 1] Ingredients Inquiry")
    input_data_1 = {
      "user_query": "Does this product contain any allergens or lead?",
      "product_id": product_id
    }
    res1 = agent.run(input_data_1)
    logger.info(f"Agent Response:\n{res1['output']}")

    # === Use Case 2: Variant/Color Inquiry ===
    logger.info("\n[Use Case 2] Available Colors")
    input_data_2 = {
      "user_query": "What colors does this come in?",
      "product_id": product_id
    }
    res2 = agent.run(input_data_2)
    logger.info(f"Agent Response:\n{res2['output']}")

    # === Edge Case: Invalid Product ID ===
    logger.info("\n[Edge Case] Invalid ID")
    input_data_bad = {
      "user_query": "Tell me about this.",
      "product_id": "NON_EXISTENT_ID_999"
    }
    res_bad = agent.run(input_data_bad)
    logger.info(f"Agent Response:\n{res_bad['output']}")

  except Exception as e:
    import traceback
    logger.error(f"Test Failed:\n{traceback.format_exc()}")

if __name__ == "__main__":
  test_expert_agent()
