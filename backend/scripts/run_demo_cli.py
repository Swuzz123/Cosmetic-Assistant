import argparse
import json
import sys
import os
import logging
import time

# Add the backend directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from app.ai.agents.orchestrator import OrchestratorAgent

# Configure logging to stdout
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("DemoRunner")

def run_demo(file_path: str):
    logger.info(f"Starting demo with file: {file_path}")
    
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        return

    agent = OrchestratorAgent()
    
    if "long_conversation" in file_path:
        logger.info("🔧 Setting low memory threshold for demo purposes...")
        agent.memory.threshold = 500  # Low threshold to trigger summary quickly

    with open(file_path, 'r') as f:
        lines = f.readlines()

    logger.info(f"Loaded {len(lines)} interaction turns.")

    for i, line in enumerate(lines):
        if not line.strip(): continue
        
        turn = json.loads(line)
        role = turn.get("role")
        content = turn.get("content")
        
        print(f"\n--- Turn {i+1} [{role}] ---")
        print(f"Content: {content}")
        
        if role == "user":
            # Pass user input to Orchestrator
            response = agent.run(content)
            print(f"🤖 Agent Reply: {response}")
            
        elif role == "assistant":
            pass

        # Small delay for readability
        time.sleep(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Orchestrator Demo")
    parser.add_argument("--file", type=str, required=True, help="Path to JSONL test data")
    args = parser.parse_args()
    
    run_demo(args.file)
