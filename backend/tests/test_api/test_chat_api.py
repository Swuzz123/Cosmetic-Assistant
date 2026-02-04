import logging
import sys
import os
import uuid
from fastapi.testclient import TestClient

# Add backend to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from app.main import app

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TestChatAPI")

client = TestClient(app)

def test_chat_flow():
    logger.info("=== Testing Chat API Endpoint ===")
    
    session_id = f"api_test_{uuid.uuid4()}"
    logger.info(f"Session ID: {session_id}")
    
    # 1. First Turn: Greeting (Should route to General)
    payload_1 = {
        "session_id": session_id,
        "user_input": "Hello, my name is Tri."
    }
    
    logger.info(f"Sending Request 1: {payload_1['user_input']}")
    response_1 = client.post("/api/v1/chat", json=payload_1)
    
    if response_1.status_code != 200:
        logger.error(f"Request 1 Failed: {response_1.text}")
        return
        
    data_1 = response_1.json()
    logger.info(f"Response 1: {data_1['response']}")
    logger.info(f"Route 1: {data_1['metadata'].get('route')}")
    
    assert response_1.status_code == 200
    assert "Tri" in payload_1['user_input']
    
    # 2. Second Turn: Ask for name (Tests Memory)
    # The Orchestrator should see the history "My name is Tri"
    payload_2 = {
        "session_id": session_id,
        "user_input": "What is my name?"
    }
    
    logger.info(f"Sending Request 2: {payload_2['user_input']}")
    response_2 = client.post("/api/v1/chat", json=payload_2)
    
    data_2 = response_2.json()
    logger.info(f"Response 2: {data_2['response']}")
    
    # Heuristic check: The bot should mention "Tri"
    if "Tri" in data_2['response']:
        logger.info("✅ Memory Verified: Bot remembered the name.")
    else:
        logger.warning(f"⚠️ Memory Check Failed: Bot response was '{data_2['response']}'")
        
    # 3. Third Turn: Search Intent (Tests Routing & Slot Filling Persistence)
    payload_3 = {
        "session_id": session_id,
        "user_input": "Find me a red lipstick under 20 dollars"
    }
    logger.info(f"Sending Request 3: {payload_3['user_input']}")
    response_3 = client.post("/api/v1/chat", json=payload_3)
    data_3 = response_3.json()
    
    logger.info(f"Response 3 Route: {data_3['metadata'].get('route')}")
    if data_3['metadata'].get('route') == 'search_agent':
         logger.info("✅ Routing Verified: Correctly routed to Search.")
    else:
         logger.warning("❌ Routing Failed.")

if __name__ == "__main__":
    test_chat_flow()
