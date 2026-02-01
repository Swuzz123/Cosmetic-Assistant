from abc import ABC, abstractmethod
from typing import Any, Dict, List

class BaseAgent(ABC):
    """
    Abstract Base Class for all agents in the system.
    This enforces a standard structure that all agents (Search, Orchestrator, etc.) must follow.
    """
    
    def __init__(self, name: str):
      self.name = name
      # TODO: Initialize LLM (LangChain/OpenAI) here
      # self.llm = ChatOpenAI(model="gpt-4o")

    @abstractmethod
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
      """
      Main method to process input and return output.
      Must be implemented by child classes.
      """
      pass

  # TODO: Add shared helper methods here (e.g., logging, error handling)
