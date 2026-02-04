import logging
import sys
import os
import uuid
from app.schemas.chat import ChatRequest
from app.core.database import SessionLocal
from app.api.v1.endpoints.chat import chat_endpoint

# Add backend to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TestPriceContext")

def test_price_context():
    logger.info("=== Testing Price Follow-up Context ===")
    
    session_id = f"price_test_{uuid.uuid4()}"
    db = SessionLocal()
    
    def send_msg(input_text):
        req = ChatRequest(session_id=session_id, user_input=input_text)
        res = chat_endpoint(req, db)
        logger.info(f"User: {input_text}")
        logger.info(f"Bot: {res.response}")
        logger.info(f"Route: {res.metadata.get('route')}")
        return res
    
    try:
        # Turn 1: Establish context (Expert Intent)
        # "Tell me about Cloud Kiss..."
        logger.info("--- Turn 1: Ask about Specific Product ---")
        res1 = send_msg("Tell me about Cloud Kiss Matte Lip Mousse.")
        
        # Turn 2: Ask about price variation (The User's Bug)
        # "Màu khác nhau vậy thì giá tiền có khác nhau không?" -> Translated/Similar intent
        logger.info("--- Turn 2: Ask if price differs by color ---")
        res2 = send_msg("Does the price differ for different colors?")
        
        # Check routing
        route = res2.metadata.get('route')
        if route == 'expert_agent':
             logger.info("✅ Route is correct: expert_agent")
        else:
             logger.warning(f"⚠️ Route might be wrong: {route}")
             
        # Check response content
        # Should provide price details or say no difference.
        if "$" in res2.response or "price" in res2.response.lower():
             logger.info("✅ Bot discussed price contextually.")
        else:
             logger.warning("⚠️ Bot might have missed the topic.")

    except Exception as e:
        logger.error(f"Test Failed: {e}", exc_info=True)
    finally:
        db.close()

if __name__ == "__main__":
    test_price_context()
