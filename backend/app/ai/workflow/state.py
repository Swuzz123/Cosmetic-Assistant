import operator
from langchain_core.messages import BaseMessage
from typing import TypedDict, Annotated, List, Dict, Any, Optional

class AgentState(TypedDict):
  """
  The shared state of the graph.
  """
  # The conversation history. 
  messages: Annotated[List[BaseMessage], operator.add]
  
  user_query: str
  
  # The next node to execute. 
  # Values: "search_node", "consultant_node", "expert_node", "general", "review"
  next: str
  
  # Structured data extracted by the Orchestrator to pass to sub-agents
  # e.g., {"brand": "MAC", "color": "red"} for SearchAgent
  agent_data: Dict[str, Any]
  
  session_context: Dict[str, Any]
  
  final_response: str
