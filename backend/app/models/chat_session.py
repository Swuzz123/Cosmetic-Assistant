from .base import Base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import Column, String, Integer, ForeignKey

class ChatSession(Base):
  __tablename__ = "chat_sessions"

  session_id = Column(String(100), primary_key=True)
  customer_id = Column(Integer, ForeignKey("customers.customer_id"))
  current_intent = Column(String(50))
  context_data = Column(JSONB)

  # Relationships
  customer = relationship("Customer", back_populates="chat_sessions")