import logging
import sys
import os
import uuid
from typing import List, Dict, Any

# Add backend to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from app.schemas.chat import ChatRequest
from app.core.database import SessionLocal
from app.api.v1.endpoints.chat import chat_endpoint
from app.models.product import ProductVariant

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TestMemoryIssue")

def test_context_loss():
    logger.info("=== Testing Context Context Loss (Recent Recommendations) ===")
    
    session_id = f"mem_test_{uuid.uuid4()}"
    db = SessionLocal()
    
    # helper
    def send_msg(input_text):
        req = ChatRequest(session_id=session_id, user_input=input_text)
        res = chat_endpoint(req, db)
        logger.info(f"User: {input_text}")
        logger.info(f"Bot: {res.response}")
        logger.info(f"Route: {res.metadata.get('route')}")
        logger.info(f"Data: {res.metadata.get('agent_data')}")
        return res
    
    try:
        # Seed some products so Consultant can find them
        p1 = "Lip Balm A"
        p2 = "Lip Balm B"
        p3 = "Lip Balm C"
        for p in [p1, p2, p3]:
            existing = db.query(ProductVariant).filter(ProductVariant.uniq_id == p).first()
            if not existing:
                db.add(ProductVariant(uniq_id=p, price=15.0, availability="In Stock", color="Clear"))
        db.commit()

        # Turn 1: Consultant/Search Recommendation (Make it explicit to ensure results)
        logger.info("--- Turn 1: Ask for recommendations ---")
        res1 = send_msg("I need to buy lip balm under 20 dollars.")
        
        # Consultant should return products.
        # We manually check if response contains product names or is generic.
        
        # Turn 2: Follow-up relying on context. Use phrasing that triggers Expert Agent.
        logger.info("--- Turn 2: Ask about 'the first one' (Expert Intent) ---")
        res2 = send_msg("Tell me more about the details of the first one.")
        
        # Should route to Expert Agent. 
        # Expert Agent should find "Lip Balm A" (first one) via context resolution.
        if "couldn't identify" in res2.response or "not found" in res2.response:
             logger.error("❌ Issue: Bot failed to identify product from context.")
        else:
             logger.info("✅ Bot handled context correctly.")
             
    except Exception as e:
        logger.error(f"Test Failed: {e}", exc_info=True)
    finally:
        db.close()

if __name__ == "__main__":
    test_context_loss()
