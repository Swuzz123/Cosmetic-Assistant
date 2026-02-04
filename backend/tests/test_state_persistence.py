import logging
import sys
import os
import uuid
import time
from app.schemas.chat import ChatRequest
from app.core.database import SessionLocal
from app.api.v1.endpoints.chat import chat_endpoint

# Add backend to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TestStatePersistence")

def test_persistence():
    logger.info("=== Testing Cross-Turn State Persistence (Sales Flow) ===")
    
    session_id = f"persist_test_{uuid.uuid4()}"
    db = SessionLocal()
    
    def send_msg(input_text):
        req = ChatRequest(session_id=session_id, user_input=input_text)
        res = chat_endpoint(req, db)
        logger.info(f"User: {input_text}")
        logger.info(f"Bot: {res.response}")
        return res
    
    try:
        # Turn 1: Buy Intent (Orchestrator extracts 'Cloud Kiss...')
        logger.info("--- Turn 1: Express Purchase Intent ---")
        res1 = send_msg("I want to buy the Cloud Kiss Matte Lip Mousse.")
        
        # Verify response confirms product
        if "Cloud Kiss" in res1.response:
             logger.info("✅ Turn 1: Product confirmed by bot.")
        else:
             logger.warning("⚠️ Turn 1: Bot didn't confirm product explicitly.")

        # Turn 2: Provide Name (Orchestrator won't extract product here, SalesAgent MUST read from Context)
        logger.info("--- Turn 2: Provide Name ---")
        res2 = send_msg("My name is John Doe.")
        
        # Check if bot still knows we are buying Cloud Kiss? 
        # Ideally it asks for Address next.
        if "address" in res2.response.lower():
             logger.info("✅ Turn 2: Bot asked for address (Flow continues).")
        else:
             logger.warning("⚠️ Turn 2: Bot lost flow?")
             
        # Turn 3: Provide Address
        logger.info("--- Turn 3: Provide Address ---")
        res3 = send_msg("123 Main St, New York")
        
        # Turn 4: Provide Phone
        logger.info("--- Turn 4: Provide Phone ---")
        res4 = send_msg("555-0199")
        
        # Final Verification: Does it create order for Cloud Kiss?
        if "Order Processed" in res4.response:
             logger.info("✅ Turn 4: Order created!")
             if "Cloud Kiss" in res4.response or "items" in res4.response:
                 logger.info("✅ Product Context Preserved till End!")
             else:
                 logger.warning("⚠️ Order created but check if product is correct.")
        else:
             logger.error("❌ Turn 4: Failed to create order.")
             
    except Exception as e:
        logger.error(f"Test Failed: {e}", exc_info=True)
    finally:
        db.close()

if __name__ == "__main__":
    test_persistence()
