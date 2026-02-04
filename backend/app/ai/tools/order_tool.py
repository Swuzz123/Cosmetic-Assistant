from typing import List, Dict, Type, Union
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field, field_validator
from app.core.database import SessionLocal
from app.services.order_service import OrderService
import json

class OrderItemInput(BaseModel):
  product_id: str = Field(..., description="The unique ID of the product variant")
  quantity: int = Field(1, description="Quantity to order")

class OrderInput(BaseModel):
  items: List[OrderItemInput] = Field(..., description="List of items to purchase")
  name: str = Field(..., description="Customer's full name")
  address: str = Field(..., description="Shipping address")
  phone: str = Field(..., description="Phone number")
  session_id: str = Field(..., description="Current Chat Session ID")

  @field_validator('items', mode='before')
  @classmethod
  def parse_items(cls, v):
    if isinstance(v, str):
      try:
        return json.loads(v)
      except json.JSONDecodeError:
        raise ValueError("items must be a valid JSON list string")
    return v

class OrderTool(BaseTool):
  name: str = "create_order"
  description: str = (
      "Use this tool to finalize a purchase when the user has confirmed products and provided shipping info. "
      "Returns the Order ID."
  )
  args_schema: Type[BaseModel] = OrderInput

  def _run(self, items: List[OrderItemInput], name: str, address: str, phone: str, session_id: str) -> str:
    session = SessionLocal()
    try:
      resolved_items = []
      from app.services.product_service import ProductService
      
      for item in items:
        product = ProductService.get_product_by_id_or_name(session, item.product_id)
        
        if product:
          resolved_id = product.product_id 
          resolved_items.append({"product_id": resolved_id, "quantity": item.quantity})
        else:
          resolved_items.append({"product_id": item.product_id, "quantity": item.quantity})

      customer_details = {"name": name, "address": address, "phone": phone}
          
      order_id = OrderService.create_order(
        session, 
        session_id=session_id, 
        customer_details=customer_details, 
        items=resolved_items
      )
      return f"Order created successfully! Order ID: #{order_id}. Total amount pending payment."
    except Exception as e:
      return f"Failed to create order: {str(e)}"
    finally:
      session.close()
