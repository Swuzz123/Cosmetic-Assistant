from typing import Any, Dict, List
from langchain_openai import ChatOpenAI
from langchain_core.agents import AgentAction, AgentFinish
from langchain_core.messages import BaseMessage
from langchain_core.tools import BaseTool
from app.core.config import settings

class BaseAgent:
	def __init__(self, tools: List[BaseTool], model_name: str = settings.MODEL_NAME):
		"""
		Initialize the agent with tools and an LLM.
		Uses Nvidia NIM (via openai-compatible endpoint) or standard OpenAI based on config.
		"""
		# Configure LLM Client
		self.llm = ChatOpenAI(
			base_url=settings.NVIDIA_BASE_URL,
			api_key=settings.NVIDIA_API_KEY,
			model=model_name,
			temperature=0.1
		)
		self.tools = tools
		self.formatted_tools = {tool.name: tool for tool in tools}

	def run(self, user_input: str) -> str:
		"""
		Default run method to be overridden or used by simple agents.
		"""
		raise NotImplementedError("Subclasses must implement the `run` method.")
