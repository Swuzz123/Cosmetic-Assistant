from typing import Dict, Any, List
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from app.ai.agents.base import BaseAgent
from app.ai.tools.order_tool import OrderTool
from app.core.logging import setup_logging

logger = setup_logging()

class SalesAgent(BaseAgent):
  def __init__(self):
    # Initialize with the OrderTool
    super().__init__([OrderTool()]) 
    self.llm_with_tools = self.llm.bind_tools(self.tools) 

  def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sales Agent Logic.
    It receives the full state, including 'agent_data' passed from Orchestrator.
    It engages in a ReAct loop (handled by BaseAgent usually, but here we customize slightly
    or rely on the standard LLM w/ Tools behavior).
    
    Since BaseAgent.run usually takes just 'user_input' string, we might need to override 
    or just construct a prompt that includes the context.
    """
    user_input = state.get("user_query", "")
    agent_data = state.get("agent_data", {})
    session_context = state.get("session_context", {})
    history = state.get("messages", [])

    # SYNC START: Update persisted context from latest Orchestrator extraction
    # If orchestrator found a target product, update our session memory
    new_target = agent_data.get("target_product")
    if new_target:
        session_context["active_product"] = new_target
        logger.info(f"Updated Session Context Active Product: {new_target}")
    
    new_price = agent_data.get("price")
    if new_price and new_price != "Unknown Price":
        session_context["active_price"] = new_price

    # Retrieve from Session Context (Persistence)
    target_product = session_context.get("active_product", "UNKNOWN")
    target_price = session_context.get("active_price", "Unknown Price")
    
    product_context_str = target_product if target_product != "UNKNOWN" else "UNKNOWN (Check Conversation History)"
    
    logger.info(f"SalesAgent activated. Persistent Target: {target_product}. Input: {user_input}")

    # Construct a specialized system prompt for Sales
    # We include the 'agent_data' in the prompt so the generic LLM knows what we are selling.
    
    sales_prompt = f"""
    You are a professional Sales Assistant for a Cosmetics Shop.
    Your goal is to finalize a purchase order.
    
    CONTEXT (PERSISTENT MEMORY):
    - User is interested in: {product_context_str}
    - Estimated Price: {target_price}
    
    NOTE: If 'User is interested in' is UNKNOWN, checking the chat history is your highest priority.
    
    CRITICAL INSTRUCTIONS:
    - You have ONLY ONE tool: 'create_order'.
    - Do NOT invent other tools like 'confirm_product'.
    - To confirm details, just ASK the user in plain text.
    - Do NOT use 'create_order' yet.
    - You must first collect the following information from the user:
      1. Full Name
      2. Shipping Address
      3. Phone Number
    
    YOUR PROTOCOL:
    1. If the user just said "I want to buy", CONFIRM the product ({product_context_str}) and price first.
    2. Then, ask for the missing details (Name, Address, Phone) one by one.
    3. ONLY when you have ALL 3 details, call the 'create_order' tool.
       - The 'items' argument for the tool must be a LIST of objects, not a string.
       - Example: items=[{{"product_id": "{product_context_str}", "quantity": 1}}]
    
    Current User Input: {user_input}
    """
    
    # Use tool binding if available (handled by BaseAgent)
    
    # Let's construct the message list properly
    messages = [SystemMessage(content=sales_prompt)] + history[-5:] + [HumanMessage(content=user_input)]
    
    # Invoke
    # Parsing the output to see if it wants to call a tool
    try:
      response = self.llm_with_tools.invoke(messages)
      
      # If response has tool_calls (AIMessage)
      if response.tool_calls:
        logger.info(f"SalesAgent triggered tool calls: {response.tool_calls}")
        # Execute tool calls
        tool_outputs = []
        for tool_call in response.tool_calls:
          tool_name = tool_call["name"]
          tool_args = tool_call["args"]
          user_session_id = agent_data.get("session_id", "unknown_session")
          tool_args["session_id"] = user_session_id
          
          if tool_name == "create_order":
            tool_instance = self.tools[0] 
            res = tool_instance.invoke(tool_args)
            tool_outputs.append(res)
          else:
            logger.warning(f"Hallucinated tool: {tool_name}")
            tool_outputs.append(f"Error: Tool '{tool_name}' does not exist. Please reply with text or use 'create_order'.")
        
        if not tool_outputs:
          return {"output": "I'm sorry, I tried to specify an action that isn't supported. Could you please confirm the details again?"}

        final_msg = f"Order Processed: {tool_outputs[0]}" 
        return {"output": final_msg}
          
      else:
        return {"output": response.content}

    except Exception as e:
      logger.error(f"SalesAgent Error: {e}")
      return {"output": "I'm having trouble processing the order. Please try again."}
