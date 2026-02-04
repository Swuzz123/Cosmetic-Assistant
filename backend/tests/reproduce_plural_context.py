import logging
import sys
import os
import uuid
from app.schemas.chat import ChatRequest
from app.core.database import SessionLocal
from app.api.v1.endpoints.chat import chat_endpoint
from app.models.product import ProductVariant

# Add backend to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TestPluralContext")

def test_plural_context():
    logger.info("=== Testing Context Context Loss (Plural/Multiple Products) ===")
    
    session_id = f"mem_test_plural_{uuid.uuid4()}"
    db = SessionLocal()
    
    # helper
    def send_msg(input_text):
        req = ChatRequest(session_id=session_id, user_input=input_text)
        res = chat_endpoint(req, db)
        logger.info(f"User: {input_text}")
        logger.info(f"Bot: {res.response}")
        logger.info(f"Route: {res.metadata.get('route')}")
        return res
    
    try:
        # Turn 1: Ask for recommendations to get multiple items in context
        # We need a query that returns multiple items.
        # "Lip balm under 20 dollars" usually returns multiple.
        logger.info("--- Turn 1: Ask for multiple products ---")
        res1 = send_msg("I need to buy lip balm under 20 dollars.")
        
        # Turn 2: Ask about "ingredients for those" (Expert Intent + Plural)
        logger.info("--- Turn 2: Ask about 'ingredients for those' (Plural Context) ---")
        res2 = send_msg("Tell me the ingredients for those products.")
        
        # Check if response mentions MULTIPLE products
        # We expect it to mention at least 2 distinct prices or names if it works correctly.
        # If it only mentions one, it failed.
        
        response_text = res2.response.lower()
        if "lippie stix" in response_text and "revlon" in response_text:
             logger.info("✅ Bot handled MULTIPLE products from context.")
        elif "lippie stix" in response_text or "revlon" in response_text:
             logger.warning("⚠️ Bot maybe only handled ONE product.")
        else:
             logger.error("❌ Bot failed to answer relevantly.")
             
    except Exception as e:
        logger.error(f"Test Failed: {e}", exc_info=True)
    finally:
        db.close()

if __name__ == "__main__":
    test_plural_context()
