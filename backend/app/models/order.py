from .base import Base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, ForeignKey, DECIMAL, TIMESTAMP, func

class Order(Base):
  __tablename__ = "orders"

  order_id = Column(Integer, primary_key=True, autoincrement=True)
  customer_id = Column(Integer, ForeignKey("customers.customer_id"))
  total_amount = Column(DECIMAL(10, 2))
  status = Column(String(50), default='pending')
  created_at = Column(TIMESTAMP, server_default=func.now())

  # Relationships
  customer = relationship("Customer", back_populates="orders")
  items = relationship("OrderItem", back_populates="order")

class OrderItem(Base):
  __tablename__ = "order_items"

  order_item_id = Column(Integer, primary_key=True, autoincrement=True)
  order_id = Column(Integer, ForeignKey("orders.order_id"))
  variant_id = Column(String(50), ForeignKey("product_variants.uniq_id"))
  quantity = Column(Integer, default=1)
  unit_price = Column(DECIMAL(10, 2))

  # Relationships
  order = relationship("Order", back_populates="items")
  variant = relationship("ProductVariant", back_populates="order_items")
