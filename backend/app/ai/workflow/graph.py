from langgraph.graph import StateGraph, END
from langchain_core.messages import AIMessage, HumanMessage

from app.ai.workflow.state import AgentState
from app.ai.agents.orchestrator import OrchestratorAgent
from app.ai.agents.search_agent import SearchAgent
from app.ai.agents.consultant_agent import ConsultantAgent
from app.ai.agents.expert_agent import ExpertAgent
from app.ai.agents.sales_agent import SalesAgent
from app.core.logging import setup_logging

logger = setup_logging()

orchestrator = OrchestratorAgent()
search_agent = SearchAgent()
consultant_agent = ConsultantAgent()
expert_agent = ExpertAgent()
sales_agent = SalesAgent()

# ------------------------------ NODE DEFINITIONS ------------------------------
def orchestrator_node(state: AgentState):
  """
  The decision maker. Analyzes user_query and routes.
  """
  user_query = state["user_query"]
  messages = state["messages"]
  
  decision = orchestrator.route(user_query, messages)
  
  return {
    "next": decision["next"],
    "agent_data": decision.get("extracted_data", {})
  }

def search_node(state: AgentState):
  query = state["user_query"]
  logger.info(f"Routing to Search Node: {query}")
  
  result = search_agent.run(query)
  response = result["output"]
  
  return {
    "final_response": response,
    "messages": [AIMessage(content=response)]
  }

def consultant_node(state: AgentState):
  query = state["user_query"]
  logger.info(f"Routing to Consultant Node: {query}")
  
  result = consultant_agent.run(query)
  response = result["output"]
  
  return {
    "final_response": response,
    "messages": [AIMessage(content=response)]
  }

def expert_node(state: AgentState):
  data = state["agent_data"]
  user_query = state["user_query"]
  product_id = data.get("product_id")
  
  messages = state.get("messages", [])
  
  logger.info(f"Routing to Expert Node. ID: {product_id}")
  
  # Pass context to ExpertAgent for resolution if ID is missing
  input_payload = {
      "user_query": user_query, 
      "product_id": product_id,
      "chat_history": messages
  }
  result = expert_agent.run(input_payload)
  response = result["output"]
  
  return {
    "final_response": response,
    "messages": [AIMessage(content=response)]
  }

def sales_node(state: AgentState):
  """
  Executes Sales Agent logic.
  Has access to full state/history + agent_data (target_product, price).
  """
  logger.info(f"Routing to Sales Node.")
  
  # Pass context to SalesAgent.run 
  result = sales_agent.run(state)
  response = result["output"]
  
  return {
    "final_response": response,
    "messages": [AIMessage(content=response)]
  }

def general_node(state: AgentState):
  query = state["user_query"]
  messages = state["messages"]
  response = orchestrator.generate_general_response(query, messages)
  return {
    "final_response": response,
    "messages": [AIMessage(content=response)]
  }

# ----------------------------- GRAPH CONSTRUCTION -----------------------------

workflow = StateGraph(AgentState)

workflow.add_node("orchestrator", orchestrator_node)
workflow.add_node("search_agent", search_node)
workflow.add_node("consultant_agent", consultant_node)
workflow.add_node("expert_agent", expert_node)
workflow.add_node("sales_agent", sales_node)
workflow.add_node("general", general_node)

workflow.set_entry_point("orchestrator")

# Conditional Edge Logic
def route_decision(state: AgentState):
  return state["next"]

workflow.add_conditional_edges(
  "orchestrator",
  route_decision,
  {
    "search_agent": "search_agent",
    "consultant_agent": "consultant_agent",
    "expert_agent": "expert_agent",
    "sales_agent": "sales_agent",
    "general": "general"
  }
)

# All leaf nodes go to END
workflow.add_edge("search_agent", END)
workflow.add_edge("consultant_agent", END)
workflow.add_edge("expert_agent", END)
workflow.add_edge("sales_agent", END)
workflow.add_edge("general", END)

# Compile
app_graph = workflow.compile()
