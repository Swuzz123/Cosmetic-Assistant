import sys
import os
import logging

# Add parent path to allow imports
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from app.ai.agents.search_agent import SearchAgent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TestSearchAgent")

def test_search_agent():
    logger.info("=== Testing SearchAgent ===")
    
    try:
        agent = SearchAgent()
        
        # Test Case 1: Specific Filter
        query = "Find me a red lipstick by MAC under 25 dollars"
        logger.info(f"User Query: {query}")
        
        response = agent.run(query)
        logger.info(f"Agent Response: {response['output']}")
        
        # Test Case 2: Vague input (Edge Case)
        query_vague = "I want something nice"
        logger.info(f"User Query: {query_vague}")
        response_vague = agent.run(query_vague)
        logger.info(f"Agent Response (Vague): {response_vague['output']}")

    except Exception:
        import traceback
        logger.error(f"Test Failed:\n{traceback.format_exc()}")

if __name__ == "__main__":
    test_search_agent()
