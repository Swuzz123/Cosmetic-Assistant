from typing import Dict, Any, List
import logging
from app.ai.agents.base import BaseAgent
from app.ai.agents.search_agent import SearchAgent
from app.ai.agents.consultant_agent import ConsultantAgent
from app.ai.agents.expert_agent import ExpertAgent
from app.ai.memory.memory_manager import MemoryManager
from app.ai.workflow.query_refiner import QueryRefiner
from app.core.logging import setup_logging
from langchain_core.messages import HumanMessage

logger = setup_logging()

class OrchestratorAgent(BaseAgent):
	def __init__(self):
		super().__init__([]) 
		self.search_agent = SearchAgent()
		self.consultant_agent = ConsultantAgent()
		self.expert_agent = ExpertAgent()
		
		self.memory = MemoryManager(self.llm)
		self.refiner = QueryRefiner(self.llm)

	def run(self, user_input: str) -> str:
		logger.info(f"Orchestrator received: {user_input}")
		
		# 1. Update Short-term Memory (User turn)
		self.memory.add_message("user", user_input)
		
		# 2. Check & Trigger Summarization
		self.memory.check_and_summarize()
		
		# 3. Refine Query (Understanding Layer)
		history_text = self.memory.get_history_text()
		refined = self.refiner.refine_query(user_input, history_text, self.memory.session_summary)
		
		logger.info(f"Refined Query Result: {refined}")
		
		if refined.get("needs_clarification"):
			questions = "\n".join(refined["clarifying_questions"])
			response_text = f"I'm not sure specifically what you mean. {questions}"
			self.memory.add_message("assistant", response_text)
			return response_text

		final_query = refined.get("rewritten_query", user_input)
		
		# 4. Routing Logic
		intent = self._classify_intent(final_query)
		logger.info(f"Routing to: {intent}")
		
		response_text = "I couldn't process that request."
		
		try:
			if intent == "SEARCH":
				res = self.search_agent.run(final_query)
				if isinstance(res, dict):
					response_text = res.get("output", str(res))
				else:
					response_text = str(res)
							
			elif intent == "EXPERT":
				response_text = "Let me check the details for that product... (Product extraction logic to be enhanced)"
				res = self.consultant_agent.run(final_query)
				if isinstance(res, dict):
					response_text = res.get("output", str(res))
				else:
					response_text = str(res)

			else: # CONSULTANT or DEFAULT
				res = self.consultant_agent.run(final_query)
				if isinstance(res, dict):
					response_text = res.get("output", str(res))
				else:
					response_text = str(res)
								
		except Exception as e:
			logger.error(f"Agent execution failed: {e}")
			response_text = "I encountered an internal error while processing your request."

		# 5. Update Memory (Assistant turn)
		self.memory.add_message("assistant", response_text)
		return response_text

	def _classify_intent(self, query: str) -> str:
		prompt = f"""
		Classify the intent of this query: "{query}"
		Options:
		- SEARCH: Specific criteria (price < 20, red color, brand MAC)
		- EXPERT: Deep specific question about a SINGLE product (ingredients, safety, how to use)
		- CONSULTANT: General advice, vague needs, "what do you recommend", "dry lips"
		
		Return ONLY the word SEARCH, EXPERT, or CONSULTANT.
		"""
		res = self.llm.invoke([HumanMessage(content=prompt)])
		return res.content.strip().upper()
