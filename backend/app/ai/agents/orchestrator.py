import json
from typing import Dict, Any, List
from langchain_core.messages import HumanMessage, BaseMessage
from app.ai.agents.base import BaseAgent
from app.utils.prompt_templates import ORCHESTRATOR_PROMPT
from app.core.logging import setup_logging

logger = setup_logging()

class OrchestratorAgent(BaseAgent):
  def __init__(self):
    super().__init__([])
  
  def route(self, user_input: str, chat_history: List[BaseMessage]) -> Dict[str, Any]:
    """
    Analyze the input and route to the correct agent.
    Returns a dictionary with 'next', 'reasoning', and 'extracted_data'.
    """
    # Format chat history as a string for context
    history_str = "\n".join([f"{msg.type.upper()}: {msg.content}" for msg in chat_history[-5:]])
    
    prompt = ORCHESTRATOR_PROMPT.format(
      user_input=user_input,
      chat_history=history_str
    )
    
    try:
      logger.info(f"Orchestrator analyzing input: {user_input}")
      
      response = self.llm.invoke([HumanMessage(content=prompt)])
      content = response.content.strip()
      
      import re
      # 1. Try to find JSON inside ```json ... ``` code blocks
      code_block_match = re.search(r"```json\s*(\{.*?\})\s*```", content, re.DOTALL)
      if code_block_match:
        json_str = code_block_match.group(1)
      else:
        json_match = re.search(r"\{.*?\}", content, re.DOTALL)
        if json_match:
          json_str = json_match.group(0)
        else:
           # Fallback to greedy if structure is complex (nested)
           greedy_match = re.search(r"\{.*\}", content, re.DOTALL)
           if greedy_match:
              json_str = greedy_match.group(0)
           else:
              raise json.JSONDecodeError("No JSON block found", content, 0)

      decision = json.loads(json_str)
      
      logger.info(f"Orchestrator decision: {decision}")
      
      return decision

    except json.JSONDecodeError:
      logger.error(f"Failed to parse Orchestrator JSON response: {content}")
      # Fallback to General if parsing fails
      return {
        "next": "general",
        "reasoning": "Failed to parse intent, defaulting to general response.",
        "extracted_data": {}
      }
    except Exception as e:
      logger.error(f"Error in Orchestrator: {e}", exc_info=True)
      return {
        "next": "general",
        "reasoning": f"Error occurred: {str(e)}",
        "extracted_data": {}
      }

  def generate_general_response(self, user_input: str, chat_history: List[BaseMessage] = []) -> str:
    """
    Handle 'general' intent directly (Greetings, Vague requests, Contextual questions).
    """
    history_str = "\n".join([f"{msg.type.upper()}: {msg.content}" for msg in chat_history[-5:]])
    
    prompt = f"""
    You are a helpful and friendly Cosmetics Assistant.
    
    Chat History:
    {history_str}
    
    The user said: "{user_input}"
    
    Instructions:
    - If it's a greeting, greet back warmly.
    - If the user asks about something discussed previously (e.g. "What is my name?"), use the Chat History to answer.
    - If it's a vague request (e.g. "I want to buy"), ask clarifying questions (budget? preferred brand? skin type?).
    - If it's completely out of scope, politely refuse.
    
    Keep it short and friendly.
    """
    res = self.llm.invoke([HumanMessage(content=prompt)])
    return res.content
