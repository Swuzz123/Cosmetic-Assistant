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
logger = logging.getLogger("TestSummary")

def test_summary_accumulation():
    logger.info("=== Testing Summary Accumulation ===")
    
    session_id = f"summ_test_{uuid.uuid4()}"
    db = SessionLocal()
    
    # We need to send > 10 messages to trigger summary. 
    # Let's simulate a conversation.
    
    for i in range(12):
        logger.info(f"--- Turn {i+1} ---")
        msg = f"This is message number {i+1} to fill up the context window."
        req = ChatRequest(session_id=session_id, user_input=msg)
        res = chat_endpoint(req, db)
        
        # Check summaries
        if res.summaries:
            logger.info(f"✅ Summaries found: {len(res.summaries)}")
            logger.info(f"Latest Summary: {res.summaries[-1][:50]}...")
            if len(res.summaries) >= 1:
                logger.info("Test Passed: Summary created and returned.")
                return

    logger.warning("Test Failed: No summaries generated after 12 turns.")

if __name__ == "__main__":
    test_summary_accumulation()
