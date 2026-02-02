from typing import Optional, Type
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
from app.core.database import SessionLocal
from app.services.product_service import ProductService

class ExpertInput(BaseModel):
  product_id: str = Field(..., description="The unique ID of the product to retrieve details for")

class ExpertTool(BaseTool):
  name: str = "get_product_details"
  description: str = (
    "Use this tool to get comprehensive technical details, ingredients, and variant info for a SPECIFIC product ID. "
    "Useful when the user asks specific questions about a product they are already viewing."
  )
  args_schema: Type[BaseModel] = ExpertInput

  def _run(self, product_id: str) -> str:
    session = SessionLocal()
    try:
      product = ProductService.get_product_by_id(session, product_id)
      if not product:
        return f"Product with ID {product_id} not found."
      
      # Format output as a readable text for the Agent
      details = (
        f"Product: {product.product_name}\n"
        f"Description: {product.description}\n"
        f"Ingredients: {product.ingredients}\n"
        f"Highlights: {product.highlights}\n"
        f"Variants Available: {len(product.variants)}\n"
      )
      
      # List variants briefly
      variants_info = "\n".join([f"- {v.color} (${v.price})" for v in product.variants[:10]])
      if len(product.variants) > 10:
        variants_info += "\n... (more variants)"
          
      return details + "\nVariants:\n" + variants_info
      
    except Exception as e:
      return f"Error retrieving product details: {str(e)}"
    finally:
      session.close()
