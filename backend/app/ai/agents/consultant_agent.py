import json
from typing import Dict, Any, List
from app.ai.agents.base import BaseAgent
from langchain_core.messages import HumanMessage
from app.ai.tools.consultant_tool import ConsultantTool
from app.utils.prompt_templates import CONSULTANT_AGENT_PROMPT
from app.core.logging import setup_logging

logger = setup_logging()

class ConsultantAgent(BaseAgent):
	def __init__(self):
		# Initialize with the ConsultantTool
		super().__init__([ConsultantTool()])
		self.tool = ConsultantTool()

	def run(self, user_input: str) -> Dict[str, Any]:
		"""
		Execute the consultant agent flow:
		1. Use ConsultantTool (Vector Search) to find relevant products.
		2. Format the prompt with user query and search results.
		3. Use LLM to generate a personalized recommendation.
		"""
		logger.info(f"ConsultantAgent received input: {user_input}")
		
		try:
			# Step 1: Get recommendations from the tool
			search_results_json = self.tool.run(user_input)
			logger.debug(f"Vector Search Raw Results: {search_results_json[:200]}...")
			
			# Step 2: Prepare the prompt
			prompt = CONSULTANT_AGENT_PROMPT.format(
				user_query=user_input,
				search_results=search_results_json
			)

			# Step 3: Invoke LLM to synthesize the response
			logger.info("Invoking LLM for synthesis...")
			response = self.llm.invoke([HumanMessage(content=prompt)])
			logger.info("ConsultantAgent generated response successfully.")
			
			return {"output": response.content}

		except Exception as e:
			logger.error(f"Error in ConsultantAgent: {e}", exc_info=True)
			return {"output": f"I apologize, I encountered an issue while trying to find recommendations: {str(e)}"}
