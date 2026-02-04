import json
from langchain_core.messages import HumanMessage
from app.core.logging import setup_logging

logger = setup_logging()

class QueryRefiner:
	"""
	Handles Ambiguity Detection, Query Rewriting, and Clarification Questions.
	"""
	def __init__(self, llm_client):
		self.llm = llm_client

	def refine_query(self, user_query: str, chat_history_text: str, session_summary: dict) -> dict:
		prompt = f"""
		You are an intelligent assistant. Your job is to understand the user's latest query in the context of the conversation.
		
		Context:
		- Session Summary: {json.dumps(session_summary)}
		- Recent Chat History: {chat_history_text}
		
		Latest User Query: "{user_query}"
		
		Task:
		1. Determine if the query is AMBIGUOUS (e.g. "that one", "red one", "is it safe?" without context).
		2. If AMBIGUOUS, try to REWRITE it using context.
		3. If you CANNOT rewrite (missing info), generate CLARIFYING QUESTIONS.
		
		Return JSON format:
		{{
			"is_ambiguous": boolean,
			"rewritten_query": "string (original query if not ambiguous)",
			"needs_clarification": boolean,
			"clarifying_questions": ["question 1", "question 2"] (empty if not needed)
		}}
		"""
		
		try:
			response = self.llm.invoke([HumanMessage(content=prompt)])
			content = response.content.strip()
			# Naive JSON extraction
			if "```json" in content:
				content = content.split("```json")[1].split("```")[0].strip()
			elif "```" in content:
				content = content.split("```")[1].split("```")[0].strip()
					
			return json.loads(content)
		except Exception as e:
				logger.error(f"Query refinement failed: {e}")
				# Fallback
				return {
					"is_ambiguous": False,
					"rewritten_query": user_query,
					"needs_clarification": False,
					"clarifying_questions": []
				}
