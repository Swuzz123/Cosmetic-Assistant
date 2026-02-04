import json
import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

from app.models.chat_session import ChatSession
from app.core.config import settings

logger = logging.getLogger("ChatHistoryService")

class ChatHistoryService:
  def __init__(self, db: Session):
    self.db = db
    self.llm = ChatOpenAI(
      base_url=settings.NVIDIA_BASE_URL,
      api_key=settings.NVIDIA_API_KEY,
      model=settings.MODEL_NAME,
      temperature=0
    )
    self.MAX_HISTORY_LENGTH = 10

  def get_messages(self, session_id: str) -> List[BaseMessage]:
    """
    Load conversation history from DB.
    """
    session = self.db.query(ChatSession).filter(ChatSession.session_id == session_id).first()
    
    if not session or not session.context_data:
      return []

    context = session.context_data
    
    # Structure: {"summary": "...", "messages": [{"role": "user", "content": "..."}]}
    summary = context.get("summary", "")
    raw_messages = context.get("messages", [])
    
    messages: List[BaseMessage] = []
    
    # Prepend Summary as System Message if it exists
    if summary:
      messages.append(SystemMessage(content=f"PREVIOUS CONVERSATION SUMMARY:\n{summary}"))
        
    # Parse recent messages
    for msg in raw_messages:
      if msg["role"] == "user":
        messages.append(HumanMessage(content=msg["content"]))
      elif msg["role"] == "assistant":
        messages.append(AIMessage(content=msg["content"]))
            
    return messages

  def get_session_context(self, session_id: str) -> Dict[str, Any]:
    """
    Retrieve the persistent session context (e.g. cart, active_product).
    """
    session = self.db.query(ChatSession).filter(ChatSession.session_id == session_id).first()
    if not session or not session.context_data:
        return {}
    return session.context_data.get("session_context", {})

  def save_messages(self, session_id: str, new_messages: List[BaseMessage], session_context: Dict[str, Any] = None):
    """
    Save new state to DB, triggering summarization if needed.
    Also saves 'session_context' if provided.
    """
    # 1. Separate Summary System Message from actual conversation
    current_summary = ""
    conversation_messages: List[BaseMessage] = []
    
    for msg in new_messages:
      if isinstance(msg, SystemMessage) and "PREVIOUS CONVERSATION SUMMARY" in msg.content:
        current_summary = msg.content.replace("PREVIOUS CONVERSATION SUMMARY:\n", "")
      else:
        conversation_messages.append(msg)
    
    # 2. Check Threshold
    summary_updated = False
    if len(conversation_messages) > self.MAX_HISTORY_LENGTH:
      logger.info(f"Session {session_id}: History length {len(conversation_messages)} > {self.MAX_HISTORY_LENGTH}. Summarizing...")
      
      # Split: Summarize the oldest half, keep the newest half
      # Preserve at least last 4 messages to keep immediate context flow
      cutoff = len(conversation_messages) - 4
      if cutoff <= 0: cutoff = 2 # Safety net
      
      msgs_to_summarize = conversation_messages[:cutoff]
      msgs_to_keep = conversation_messages[cutoff:]
      
      # Generate new summary
      new_summary_text = self._summarize(current_summary, msgs_to_summarize)
      
      current_summary = new_summary_text
      conversation_messages = msgs_to_keep
      summary_updated = True
    
    # 3. Serialize for DB
    serialized_messages = []
    for msg in conversation_messages:
      role = "user" if isinstance(msg, HumanMessage) else "assistant"
      serialized_messages.append({"role": role, "content": msg.content})
    
    # Load existing context to check for 'summary_history'
    # Since we are overwriting context_data structure, we need to preserve the history list
    # Retrieve existing session to get old history
    existing_session = self.db.query(ChatSession).filter(ChatSession.session_id == session_id).first()
    existing_summary_history = []
    if existing_session and existing_session.context_data:
        existing_summary_history = existing_session.context_data.get("summary_history", [])

    if summary_updated:
        logger.info(f"Appending new summary. History len was: {len(existing_summary_history)}")
        existing_summary_history.append(current_summary)

    final_context_data = {
      "summary": current_summary,
      "summary_history": existing_summary_history,
      "messages": serialized_messages
    }
    
    if session_context is not None:
        final_context_data["session_context"] = session_context
    else:
        # Preserve existing session_context
        existing_ctx = self.get_session_context(session_id)
        final_context_data["session_context"] = existing_ctx
        
    # 4. Save to DB
    session = self.db.query(ChatSession).filter(ChatSession.session_id == session_id).first()
    if not session:
      session = ChatSession(session_id=session_id, context_data=final_context_data)
      self.db.add(session)
    else:
      session.context_data = final_context_data
        
    self.db.commit()
    logger.info(f"Session {session_id} saved. Summary len: {len(current_summary)}. Msg count: {len(serialized_messages)}")

  def get_all_summaries(self, session_id: str) -> List[str]:
    """Return list of all past summaries"""
    session = self.db.query(ChatSession).filter(ChatSession.session_id == session_id).first()
    if not session or not session.context_data:
        return []
    return session.context_data.get("summary_history", [])

  def _summarize(self, current_summary: str, messages: List[BaseMessage]) -> str:
    """
    Helper to run summarization chain.
    """
    conversation_text = ""
    for msg in messages:
      role = "Human" if isinstance(msg, HumanMessage) else "AI"
      conversation_text += f"{role}: {msg.content}\n"
        
    prompt = ChatPromptTemplate.from_template(
      """
      You are a helpful assistant encapsulating conversation history.
      
      Current Summary of previous history:
      {current_summary}
      
      New Lines of conversation to merge into summary:
      {new_lines}
      
      INSTRUCTIONS:
      Create a concise updated summary that combines the Current Summary and New Lines.
      Focus on key facts, user preferences (skin type, budget, specific requests), and current status.
      Do not lose important details like Product IDs or addresses.
      
      New Summary:
      """
    )
    
    chain = prompt | self.llm
    response = chain.invoke({
      "current_summary": current_summary or "None",
      "new_lines": conversation_text
    })
    
    return response.content.strip()

  def create_session(self, session_id: str, customer_id: Optional[int] = None):
    """Helper to init session if not exists"""
    existing = self.db.query(ChatSession).filter(ChatSession.session_id == session_id).first()
    if not existing:
      new_session = ChatSession(
        session_id=session_id, 
        customer_id=customer_id,
        context_data={"summary": "", "messages": []}
      )
      self.db.add(new_session)
      self.db.commit()
      return new_session
    return existing
