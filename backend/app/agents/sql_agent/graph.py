from typing import Literal
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

from app.core.config import settings
from app.agents.sql_agent.state import SqlAgentState
from app.agents.sql_agent.tools import search_products_by_sql, get_product_details, check_inventory
from app.agents.sql_agent.prompts import SQL_AGENT_SYSTEM_PROMPT

# ============================== GRAPH NODES ==============================

def get_model():
    """
    Initialize the LLM model.
    Using NVIDIA NIM (OpenAI Compatible) as configured in settings.
    """
    if not settings.OPENAI_API_KEY:
        # Fallback or error handling
        print("Warning: OPENAI_API_KEY not found. Agent may fail.")
        
    llm = ChatOpenAI(
        model=settings.MODEL_NAME,
        openai_api_key=settings.OPENAI_API_KEY,
        openai_api_base=settings.OPENAI_BASE_URL,
        temperature=0
    )
    return llm

def agent_node(state: SqlAgentState):
    """
    The main agent node that decides what to do.
    """
    model = get_model()
    tools = [search_products_by_sql, get_product_details, check_inventory]
    
    # Bind tools to the model
    model_with_tools = model.bind_tools(tools)
    
    # Create the prompt template
    prompt = ChatPromptTemplate.from_messages([
        ("system", SQL_AGENT_SYSTEM_PROMPT),
        ("placeholder", "{messages}"),
    ])
    
    # Chain: Prompt -> Model
    chain = prompt | model_with_tools
    
    # Invoke
    response = chain.invoke({"messages": state["messages"]})
    
    return {"messages": [response]}

def should_continue(state: SqlAgentState) -> Literal["tools", "__end__"]:
    """
    Conditional edge to determine if we should run tools or end.
    """
    messages = state["messages"]
    last_message = messages[-1]
    
    # If the LLM requested a tool call, go to 'tools' node
    if last_message.tool_calls:
        return "tools"
    
    # Otherwise, stop
    return "__end__"

# ============================== GRAPH CONSTRUCTION ==============================

def create_sql_agent_graph():
    workflow = StateGraph(SqlAgentState)
    
    # Define Nodes
    workflow.add_node("agent", agent_node)
    
    # Prebuilt ToolNode automatically handles tool execution and output
    tool_node = ToolNode([search_products_by_sql, get_product_details, check_inventory])
    workflow.add_node("tools", tool_node)
    
    # Define Edges
    workflow.set_entry_point("agent")
    
    workflow.add_conditional_edges(
        "agent",
        should_continue,
    )
    
    # From tools, always go back to agent to interpret the result
    workflow.add_edge("tools", "agent")
    
    # Compile
    app = workflow.compile()
    return app
