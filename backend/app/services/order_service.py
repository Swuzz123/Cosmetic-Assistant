from sqlalchemy.orm import Session
from typing import List, Dict, Any
import logging
from app.models.order import Order, OrderItem
from app.models.product import ProductVariant
from app.models.customer import Customer

logger = logging.getLogger("OrderService")

class OrderService:
  @staticmethod
  def create_order(
    db: Session,
    session_id: str,
    customer_details: Dict[str, str],
    items: List[Dict[str, Any]]
  ) -> str:
    """
    Creates an order from the cart items.
    
    Args:
        db: Database session
        session_id: Chat session ID
        customer_details: Dict containing 'name', 'address', 'phone'
        items: List of dicts {'product_id': str, 'quantity': int}
        
    Returns:
        Order ID (str) or raises Exception
    """
    try:
      logger.info(f"Creating order for session {session_id}. Items: {items}")
      
      # 1. Calculate Total Amount & Verify Stock (Simplified)
      total_amount = 0.0
      order_items_objects = []
      
      for item in items:
        variant_id = item["product_id"]
        quantity = item.get("quantity", 1)
        
        # Fetch Variant to get price
        # Strategy:
        # 1. Try to find precise Variant by uniq_id
        # 2. If not found, try to find by parent product_id and pick the first available variant
        
        variant = db.query(ProductVariant).filter(ProductVariant.uniq_id == variant_id).first()
        
        if not variant:
            # Fallback: Is this a Product ID?
            first_variant = db.query(ProductVariant).filter(ProductVariant.product_id == variant_id).first()
            if first_variant:
                variant = first_variant
                logger.info(f"Resolved Product ID {variant_id} to Default Variant {variant.uniq_id}")
            else:
                raise ValueError(f"Product ID/Variant ID {variant_id} not found.")
        
        # Check Stock (Simplified check on availability text)
        if "out of stock" in str(variant.availability).lower():
            raise ValueError(f"Product {variant_id} is out of stock.")
        
        price = float(variant.price)
        line_total = price * quantity
        total_amount += line_total
        
        # Create OrderItem object
        order_item = OrderItem(
          variant_id=str(variant.uniq_id),
          quantity=quantity,
          unit_price=price
        )
        order_items_objects.append(order_item)
      
      # 2. Get or Create Customer (Simplified)
      customer_name = customer_details.get("name", "Guest")
      
      # 3. Create Order
      new_order = Order(
        total_amount=total_amount,
        status="pending"
      )
      
      db.add(new_order)
      db.flush() # Generate Order ID
      
      # 4. Link Items
      for obj in order_items_objects:
        obj.order_id = new_order.order_id
        db.add(obj)
          
      db.commit()
      
      logger.info(f"Order created successfully: {new_order.order_id}")
      return str(new_order.order_id)
        
    except Exception as e:
      db.rollback()
      logger.error(f"Failed to create order: {e}")
      raise e
