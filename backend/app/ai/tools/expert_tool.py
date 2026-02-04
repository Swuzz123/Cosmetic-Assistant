import json
import logging
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
      # Use enhanced lookup (ID or Name) to support context resolution
      product = ProductService.get_product_by_id_or_name(session, product_id)
      
      if not product:
        logging.warning(f"Product ID {product_id} not found.")
        return json.dumps({"error": "Product not found"})

      # Serialize product data
      data = {
        "product_id": product.product_id,
        "name": product.product_name,
        "description": product.description,
        "highlights": product.highlights,
        "ingredients": product.ingredients,
        "variants": []
      }

      # Add variants if available (Lazy Loading via relationship access)
      if hasattr(product, "variants") and product.variants:
        for v in product.variants:
          data["variants"].append({
            "color": v.color,
            "size": v.size,
            "price": float(v.price) if v.price else None,
            "availability": v.availability
          })
      
      return json.dumps(data, indent=2, ensure_ascii=False)

    except Exception as e:
      logging.error(f"Error fetching product details: {e}", exc_info=True)
      return json.dumps({"error": f"Internal error: {str(e)}"})
    finally:
      session.close()
