from .base import Base
from pgvector.sqlalchemy import Vector
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import Column, String, Text, Integer, ForeignKey, DECIMAL, TIMESTAMP, func

class Product(Base):
  __tablename__ = "products"

  product_id = Column(String(50), primary_key=True) 
  brand_id = Column(Integer, ForeignKey("brands.brand_id"))
  product_name = Column(String(255), nullable=False)
  description = Column(Text)
  ingredients = Column(Text)
  highlights = Column(Text)
  embedding = Column(Vector(768)) 
  created_at = Column(TIMESTAMP, server_default=func.now())

  # Relationships
  brand = relationship("Brand", back_populates="products")
  variants = relationship("ProductVariant", back_populates="product", cascade="all, delete-orphan")

class ProductVariant(Base):
  __tablename__ = "product_variants"

  uniq_id = Column(String(50), primary_key=True)
  product_id = Column(String(50), ForeignKey("products.product_id", ondelete="CASCADE"))
  color = Column(String(255))
  size = Column(String(50))
  price = Column(DECIMAL(10, 2))
  availability = Column(String(50))
  primary_image_url = Column(Text)

  # Relationships
  product = relationship("Product", back_populates="variants")
  order_items = relationship("OrderItem", back_populates="variant")
