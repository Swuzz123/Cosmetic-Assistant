import sys
import os
from dotenv import load_dotenv

# Add backend to path so we can import 'app'
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Load .env
env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../.env'))
print(f"Loading .env from: {env_path}")
load_dotenv(env_path)

# Import the Graph
try:
    from app.agents.sql_agent.graph import create_sql_agent_graph
    from langchain_core.messages import HumanMessage
except ImportError as e:
    print(f"Import Error: {e}")
    print("Ensure you have installed: langchain langgraph langchain-google-genai")
    sys.exit(1)

print("\n--- Testing SQL Agent Graph ---")

def test_agent(query: str):
    print(f"\nUser: {query}")
    app = create_sql_agent_graph()
    
    # Run the graph
    inputs = {"messages": [HumanMessage(content=query)]}
    try:
        # Stream output to see steps
        for output in app.stream(inputs):
            for key, value in output.items():
                print(f"--- Node: {key} ---")
                # Value is likely a dictionary with 'messages' list
                if "messages" in value:
                    for msg in value["messages"]:
                        print(f"[{type(msg).__name__}]: {msg.content}")
                        if hasattr(msg, 'tool_calls') and msg.tool_calls:
                            print(f"  Tool Calls: {msg.tool_calls}")
                else:
                     print(value)
    except Exception as e:
        print(f"Execution Error: {e}")

# Test Cases
if __name__ == "__main__":
    # Case 1: Simple Search
    test_agent("Find me a red lipstick under 15 dollars")
    
    # Case 2: Comparison (requires reasoning)
    # test_agent("Compare the price of Revlon vs MAC")
