from typing import Optional, Type
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
from app.core.database import SessionLocal
from app.services.vector_service import VectorService
import json

class ConsultantInput(BaseModel):
  query: str = Field(..., description="User's query or description of needs (e.g. 'lipstick for dry skin', 'party look')")
  top_k: int = Field(5, description="Number of results to return")

class ConsultantTool(BaseTool):
  name: str = "recommend_products"
  description: str = (
    "Use this tool to recommend products based on user needs, skin type, occasions, or benefits. "
    "Ideal for vague requests like 'I want something moisturizing' or 'lipstick for work'."
  )
  args_schema: Type[BaseModel] = ConsultantInput

  def _run(self, query: str, top_k: int = 5) -> str:
    session = SessionLocal()
    try:
      # Instantiate service (it handles embedding internally)
      service = VectorService()
      results = service.search_similar_products(session, query, top_k)
      
      if not results:
        return "No relevant recommendation found."
      
      return json.dumps(results, indent=2, ensure_ascii=False)
    except Exception as e:
      return f"Error executing recommendation: {str(e)}"
    finally:
      session.close()
