from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class ChatRequest(BaseModel):
  session_id: str = Field(..., description="Unique identifier for the chat session")
  user_input: str = Field(..., description="The user's message")
  platform_user_id: Optional[str] = Field(None, description="Platform specific user ID (e.g. from Facebook/Telegram)")

class ChatResponse(BaseModel):
  session_id: str
  response: str
  metadata: Optional[Dict[str, Any]] = {}
  summaries: Optional[list[str]] = []
