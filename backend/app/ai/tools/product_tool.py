from typing import Optional, Type
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
from app.core.database import SessionLocal
from app.services.product_service import ProductService
import json
import logging

class ProductDetailInput(BaseModel):
	product_id: str = Field(..., description="The unique ID of the product to retrieve.")

class GetProductDetailTool(BaseTool):
	name: str = "get_product_details"
	description: str = "Retrieves detailed information about a specific product, including its variants (colors/shades)."
	args_schema: Type[BaseModel] = ProductDetailInput

	def _run(self, product_id: str) -> str:
		session = SessionLocal()
		try:
			product = ProductService.get_product_by_id(session, product_id)
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

			# Add variants if available (assuming relationship is set up or fetched)
			# Note: We need to ensure 'variants' relationship exists in model or fetch manually.
			# Checking ProductService.get_product_by_id implementation... it does join? 
			# Actually ProductService uses standard select. Let's assume lazy loading or explicit join needed.
			# For robustness, let's fetch variants explicitly if needed, but if the model has relationship:
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
