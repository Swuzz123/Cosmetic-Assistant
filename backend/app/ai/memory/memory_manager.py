from typing import List, Dict, Any, Optional
import json
import logging
from app.ai.agents.base import BaseAgent
from langchain_core.messages import HumanMessage
from app.core.logging import setup_logging

logger = setup_logging()

class MemoryManager:
	"""
	Manages session memory, including short-term history and summarization triggering.
	"""
	def __init__(self, llm_client, summarization_threshold: int = 2000):
		"""
		Args:
				llm_client: The LLM client to use for summarization.
				summarization_threshold: Approx number of characters to trigger summary.
		"""
		self.llm = llm_client
		self.threshold = summarization_threshold
		self.chat_history: List[Dict[str, str]] = []
		self.session_summary: Dict[str, Any] = {
			"user_profile": {"prefs": [], "constraints": []},
			"key_facts": [],
			"current_intent": None
		}

	def add_message(self, role: str, content: str):
		self.chat_history.append({"role": role, "content": content})

	def get_history_text(self) -> str:
		return "\n".join([f"{msg['role']}: {msg['content']}" for msg in self.chat_history])

	def check_and_summarize(self) -> bool:
		"""
		Checks if history exceeds threshold. If so, triggers summarization.
		Returns True if summarization occurred.
		"""
		full_text = self.get_history_text()
		current_len = len(full_text)
		
		logger.debug(f"Current Context Length: {current_len} / {self.threshold}")

		if current_len > self.threshold:
			logger.info("Context length exceeded threshold. Triggering Summarization...")
			self._summarize(full_text)
			self._prune_history()
			return True
		return False

	def _summarize(self, context_text: str):
		prompt = f"""
		Analyze the following conversation and update the session summary JSON.
		Keep existing info if still relevant, add new info.
		
		Current Summary: {json.dumps(self.session_summary)}
		
		New Conversation:
		{context_text}
		
		Output a JSON with the following schema:
		{{
			"user_profile": {{ "prefs": ["..."], "constraints": ["..."] }},
			"key_facts": ["..."],
			"current_intent": "..."
		}}
		"""
		try:
			response = self.llm.invoke([HumanMessage(content=prompt)])
			content = response.content.strip()

			if "```json" in content:
					content = content.split("```json")[1].split("```")[0].strip()
			elif "```" in content:
					content = content.split("```")[1].split("```")[0].strip()
			
			new_summary = json.loads(content)
			self.session_summary = new_summary
			logger.info(f"Session Summarized: {self.session_summary}")
		except Exception as e:
				logger.error(f"Summarization failed: {e}")

	def _prune_history(self):
		keep_count = 2
		if len(self.chat_history) > keep_count * 2:
			self.chat_history = self.chat_history[-(keep_count*2):]
			logger.info(f"Pruned history. New size: {len(self.chat_history)}")
