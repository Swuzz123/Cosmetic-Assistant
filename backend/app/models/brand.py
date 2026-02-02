from .base import Base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String

class Brand(Base):
  __tablename__ = "brands"

  brand_id = Column(Integer, primary_key=True, autoincrement=True)
  brand_name = Column(String(255), unique=True, nullable=False)

  # Relationships
  products = relationship("Product", back_populates="brand")
