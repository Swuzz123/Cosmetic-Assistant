import json
from typing import Dict, Any, Union
from app.ai.agents.base import BaseAgent
from langchain_core.messages import HumanMessage
from app.ai.tools.product_tool import GetProductDetailTool
from app.utils.prompt_templates import EXPERT_AGENT_PROMPT
from app.core.logging import setup_logging

logger = setup_logging()

class ExpertAgent(BaseAgent):
	def __init__(self):
		super().__init__([GetProductDetailTool()])
		self.tool = GetProductDetailTool()

	def run(self, input_data: Union[str, Dict[str, Any]]) -> Dict[str, Any]:
		"""
		Execute the Expert Agent.
		
		Args:
				input_data: Can be a dictionary {"user_query": "...", "product_id": "..."} 
										or a JSON string representing that dictionary.
		"""
		logger.info(f"ExpertAgent received input: {input_data}")
		
		try:
			# Parse Input
			if isinstance(input_data, str):
				try:
					data = json.loads(input_data)
				except json.JSONDecodeError:
					# Fallback if just a string is passed (unlikely for this agent, but safe handling)
					logger.warning("ExpertAgent received raw string input, missing product_id context.")
					return {"output": "I need to know which product you are referring to. Please provide a product ID context."}
			else:
				data = input_data

			user_query = data.get("user_query")
			product_id = data.get("product_id")

			if not product_id:
				logger.warning("Missing product_id in input.")
				return {"output": "I cannot answer questions without knowing which product you are asking about."}

			# Step 1: Fetch Product Details
			logger.debug(f"Fetching details for Product ID: {product_id}")
			product_details_json = self.tool.run(product_id)
			
			# Check for error in tool response
			if "Product not found" in product_details_json or '{"error":' in product_details_json:
				logger.warning(f"Product ID {product_id} not found in DB.")
				if "Product not found" in product_details_json:
					return {"output": "I'm sorry, I couldn't find the details for this specific product in our database."}

			logger.debug(f"Product Details fetched: {product_details_json[:200]}...")

			# Step 2: Format Prompt
			prompt = EXPERT_AGENT_PROMPT.format(
				user_query=user_query,
				product_details=product_details_json
			)

			# Step 3: LLM Inference
			logger.info("Invoking LLM for expert explanation...")
			response = self.llm.invoke([HumanMessage(content=prompt)])
			logger.info("ExpertAgent generated response successfully.")

			return {"output": response.content}

		except Exception as e:
			logger.error(f"Error in ExpertAgent: {e}", exc_info=True)
			return {"output": f"I encountered an error analyzing the product: {str(e)}"}
