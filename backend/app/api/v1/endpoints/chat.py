from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from langchain_core.messages import HumanMessage

from app.core.database import get_sync_db
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_history import ChatHistoryService
from app.ai.workflow.graph import app_graph
from app.core.logging import setup_logging

logger = setup_logging()

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest, db: Session = Depends(get_sync_db)):
  """
  Main Chat Endpoint.
  1. Loads history from DB (if exists)
  2. Runs the Orchestrator Graph
  3. Saves new history (with summarization if needed)
  4. Returns response
  """
  try:
    session_id = request.session_id
    user_input = request.user_input
    
    logger.info(f"Received chat request. Session: {session_id}. Input: {user_input}")
    
    # 1. Initialize Service & Load History
    history_service = ChatHistoryService(db)
    
    # Ensure session exists (create if not)
    history_service.create_session(session_id)
    
    # Get past messages (including summary as SystemMessage)
    history = history_service.get_messages(session_id)
    session_context = history_service.get_session_context(session_id)
    
    # 2. Prepare Graph Input
    current_messages = history + [HumanMessage(content=user_input)]
    
    initial_state = {
      "messages": current_messages,
      "user_query": user_input,
      "next": "",
      "agent_data": {},
      "session_context": session_context, # Inject persistent context
      "final_response": ""
    }
    
    # 3. Run Graph
    logger.info(f"Invoking Agent Graph. Initial Context: {session_context}")
    final_state = app_graph.invoke(initial_state)
    
    bot_response = final_state.get("final_response", "I'm sorry, I encountered an error.")
    
    # 4. Save History & Context
    # The graph returns the full updated 'messages' list in final_state["messages"]
    updated_messages = final_state["messages"]
    updated_context = final_state.get("session_context", {})
    
    history_service.save_messages(session_id, updated_messages, updated_context)
    
    return ChatResponse(
      session_id=session_id,
      response=bot_response,
      metadata={"route": final_state.get("next"), "agent_data": final_state.get("agent_data")},
      summaries=history_service.get_all_summaries(session_id)
    )
      
  except Exception as e:
    logger.error(f"Error in chat endpoint: {e}", exc_info=True)
    raise HTTPException(
      status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
      detail=str(e)
    )
