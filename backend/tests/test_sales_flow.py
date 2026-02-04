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

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TestSalesFlow")

def test_sales_conversation():
    logger.info("=== Testing Sales Conversation Flow ===")
    
    session_id = f"sales_test_{uuid.uuid4()}"
    db = SessionLocal()
    
    # Seeding a product for testing
    from app.models.product import ProductVariant
    test_product_id = "Mac Ruby Woo lipstick"
    existing = db.query(ProductVariant).filter(ProductVariant.uniq_id == test_product_id).first()
    if not existing:
        db.add(ProductVariant(uniq_id=test_product_id, price=20.0, availability="In Stock", color="Red"))
        db.commit()
    
    # helper
    def send_msg(input_text):
        req = ChatRequest(session_id=session_id, user_input=input_text)
        res = chat_endpoint(req, db)
        logger.info(f"User: {input_text}")
        logger.info(f"Bot: {res.response}")
        logger.info(f"Route: {res.metadata.get('route')}")
        return res
    
    try:
        # 1. Trigger Sales Intent (Direct Buy)
        # Note: Assuming product exists. We should pick a real one or mocking ID might fail in OrderService 
        # but let's see if Orchestrator catches it first.
        # "Buy Mac Ruby Woo"
        # Since we don't know exact ID unless we search, let's try a generic buy that triggers Sales Agent 
        # and Sales Agent might ask for confirmation.
        
        # We assume we have a ProductVariant with ID "1" or similar in DB seeding?
        # Let's interact naturally.
        
        # Turn 1: Search to ensure item context (optional but realistic)
        # send_msg("Find me red lipstick Mac")
        
        # Turn 2: Buy
        res = send_msg("I want to buy the Mac Ruby Woo lipstick for 20 dollars")
        
        # Verify Orchestrator routed to 'sales_agent'
        if res.metadata.get("route") == "sales_agent":
            logger.info("✅ Orchestrator routed to Sales Agent")
        else:
            logger.error(f"❌ Failed routing to Sales Agent. Got: {res.metadata.get('route')}")
            return

        # Turn 3: User provides Name
        # Sales Agent should be asking for slots in the response loop.
        # Let's assume bot asked for confirmation or details.
        
        res = send_msg("Yes, that's correct. My name is John Doe.")
        if res.metadata.get("route") == "sales_agent":
             logger.info("✅ Maintained Sales State")
             
        # Turn 4: Address
        res = send_msg("123 Test Street, New York")
        
        # Turn 5: Phone
        res = send_msg("555-0199")
        
        # Turn 6: Handle potential product re-confirmation
        # If Bot asks "What product?", we reply.
        if "what product" in res.response.lower() or "confirm the product" in res.response.lower():
             logger.info("ℹ️ Bot asked for product confirmation. Replying...")
             res = send_msg("Mac Ruby Woo lipstick")
        
        # At this point, or next, Order should be created.
        if "Order created" in res.response or "Order Processed" in res.response:
            logger.info("✅ Order Created successfully")
        else:
            logger.info("⚠️ Order might not be created yet, check logs.")
            
    except Exception as e:
        logger.error(f"Test Failed: {e}", exc_info=True)
    finally:
        db.close()

if __name__ == "__main__":
    test_sales_conversation()
