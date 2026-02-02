from typing import Optional, Type
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
from app.core.database import SessionLocal
from app.services.search_service import SearchService
import json

class SearchInput(BaseModel):
  brand: Optional[str] = Field(None, description="Brand name to filter by (e.g. 'Mac', 'Revlon')")
  price_min: Optional[float] = Field(None, description="Minimum price")
  price_max: Optional[float] = Field(None, description="Maximum price")
  color: Optional[str] = Field(None, description="Color name to filter by (e.g. 'Red', 'Nude')")

class SearchTool(BaseTool):
  name: str = "search_cosmetics"
  description: str = (
    "Use this tool to find cosmetics based on EXPLICIT criteria like brand, price, or color. "
    "Do not use this for vague requests or advice."
  )
  args_schema: Type[BaseModel] = SearchInput

  def _run(
    self, 
    brand: Optional[str] = None, 
    price_min: Optional[float] = None, 
    price_max: Optional[float] = None, 
    color: Optional[str] = None
  ) -> str:
    session = SessionLocal()
    try:
      results = SearchService.search_products(
        session, 
        brand_name=brand, 
        price_min=price_min, 
        price_max=price_max, 
        color=color
      )
      if not results:
        return "No products found matching the criteria."
      return json.dumps(results, indent=2, ensure_ascii=False)
    except Exception as e:
      return f"Error executing search: {str(e)}"
    finally:
      session.close()
