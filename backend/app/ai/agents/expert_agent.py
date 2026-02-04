import json
from typing import Dict, Any, Union
from app.ai.agents.base import BaseAgent
from langchain_core.messages import HumanMessage
from app.ai.tools.expert_tool import ExpertTool
from app.utils.prompt_templates import EXPERT_AGENT_PROMPT
from app.core.logging import setup_logging

logger = setup_logging()

class ExpertAgent(BaseAgent):
	def __init__(self):
		super().__init__([ExpertTool()])
		self.tool = ExpertTool()

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
			chat_history = data.get("chat_history", [])
			session_context = data.get("session_context", {})

			# List of products to process
			target_products = []
			if product_id:
				target_products.append(product_id)
      
			# Fallback: Check Persistent Session Context
			if not target_products:
				persistent_product = session_context.get("active_product")
				if persistent_product and persistent_product != "UNKNOWN":
					logger.info(f"Using Persistent Session Product: {persistent_product}")
					target_products.append(persistent_product)

			# Context Resolution: If missing or we want to double check history for plural
			if not target_products and chat_history:
				logger.info("Product ID missing. Attempting to resolve from Chat History...")
				recent_msgs = chat_history[-3:] # Look at last 3 messages (User, Bot, User)
				
				history_str = "\n".join([f"{m.type.upper()}: {m.content}" for m in recent_msgs])
				
				resolution_prompt = f"""
				You are an intelligent internal helper.
				The user asked: "{user_query}"
				
				Recent Chat History:
				{history_str}
				
				Identify the specific product(s) the user is definitely referring to.
				If the user says "those three types", look for the list of products mentioned by the AI previously.
				
				RETURN JSON format ONLY:
				{{
					"found": true/false,
					"product_names": ["product A", "product B"]
				}}
				"""
				try:
					res_msg = self.llm.invoke([HumanMessage(content=resolution_prompt)])
					import re
					json_match = re.search(r"\{.*\}", res_msg.content, re.DOTALL)
					if json_match:
						resolved = json.loads(json_match.group(0))
						if resolved.get("found"):
							names = resolved.get("product_names", [])
							if isinstance(names, list):
								target_products.extend(names)
							elif isinstance(names, str):
								target_products.append(names)
							
							logger.info(f"Resolved context to products: {target_products}")
				except Exception as e:
					logger.warning(f"Context resolution failed: {e}")

			if not target_products:
				logger.warning("No products identified in input or context.")
				return {"output": "I cannot answer questions without knowing which product you are asking about."}

			# Step 1: Fetch Product Details (Loop for multiple)
			all_product_details = []
			for p_id in target_products:
				logger.debug(f"Fetching details for Product: {p_id}")
				details_json = self.tool.run({"product_id": str(p_id)})
				
				if "Product not found" in details_json:
					logger.warning(f"Product {p_id} not found in DB.")
					continue
					
				all_product_details.append(f"--- Details for {p_id} ---\n{details_json}\n")

			if not all_product_details:
				return {"output": "I'm sorry, I couldn't find details for any of the mentioned products."}

			combined_details = "\n".join(all_product_details)

			# Step 2: Format Prompt
			prompt = EXPERT_AGENT_PROMPT.format(
				user_query=user_query,
				product_details=combined_details
			)

			# Step 3: LLM Inference
			logger.info("Invoking LLM for expert explanation...")
			response = self.llm.invoke([HumanMessage(content=prompt)])
			logger.info("ExpertAgent generated response successfully.")

			return {"output": response.content}

		except Exception as e:
			logger.error(f"Error in ExpertAgent: {e}", exc_info=True)
			return {"output": f"I encountered an error analyzing the product: {str(e)}"}
