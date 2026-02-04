import logging
from langchain_core.messages import HumanMessage

from app.ai.workflow.graph import app_graph

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TestWorkflow")

def test_workflow():
  logger.info("=== Testing Orchestrator Workflow ===")
  
  test_cases = [
    {
      "name": "General Greeting",
      "input": "Hello, are you there?",
      "expected_node": "general"
    },
    {
      "name": "Search Intent",
      "input": "Find me a red lipstick under 20 dollars",
      "expected_node": "search_agent"
    },
    {
      "name": "Consultant Intent",
      "input": "My lips are very dry, what do you recommend?",
      "expected_node": "consultant_agent"
    },
    {
      "name": "Expert Intent (Explicit)",
      "input": "Tell me about product ID 12345",
      "expected_node": "expert_agent"
    }
  ]
  
  for case in test_cases:
    logger.info(f"\n--- Testing: {case['name']} ---")
    user_input = case["input"]
    
    # Invoke the graph
    # initial state
    initial_state = {
      "messages": [HumanMessage(content=user_input)],
      "user_query": user_input,
      "next": "",
      "agent_data": {},
      "final_response": ""
    }
    
    try:
      # We use stream or invoke. Invoke returns the final state.
      final_state = app_graph.invoke(initial_state)
      
      logger.info(f"Final Response: {final_state['final_response']}")
      logger.info(f"Route taken: {final_state['next']}")
      
      if final_state["next"] == case["expected_node"]:
        logger.info("Routing Correct")
      else:
        logger.warning(f"Routing Mismatch. Expected {case['expected_node']}, Got {final_state['next']}")
            
    except Exception as e:
      logger.error(f"Test Failed: {e}")

if __name__ == "__main__":
  test_workflow()
