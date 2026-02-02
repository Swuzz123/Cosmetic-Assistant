from .base import Base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import Column, Integer, String, TIMESTAMP, func, ForeignKey

class Customer(Base):
  __tablename__ = "customers"

  customer_id = Column(Integer, primary_key=True, autoincrement=True)
  platform_user_id = Column(String(255), unique=True, nullable=False)
  full_name = Column(String(100))
  skin_profile = Column(JSONB)  # {"tone": "warm", "problem": "dry"}
  created_at = Column(TIMESTAMP, server_default=func.now())

  # Relationships
  chat_sessions = relationship("ChatSession", back_populates="customer")
  orders = relationship("Order", back_populates="customer")