import json
from typing import Dict, Any
from app.ai.agents.base import BaseAgent
from langchain_core.messages import HumanMessage
from app.ai.tools.search_tool import SearchTool
from app.utils.prompt_templates import SEARCH_AGENT_PROMPT
from app.core.logging import setup_logging

logger = setup_logging()

class SearchAgent(BaseAgent):
  def __init__(self):
    super().__init__([SearchTool()])
    self.tool = SearchTool()

  def run(self, user_input: str) -> Dict[str, Any]:
    """
    Execute the agent with user input using manual JSON extraction.
    This bypasses LangChain's bind_tools issues.
    """
    logger.info(f"SearchAgent received input: {user_input}")
    prompt = SEARCH_AGENT_PROMPT.format(user_input=user_input)
    try:
      response = self.llm.invoke([HumanMessage(content=prompt)])
      content = response.content.strip()
      logger.debug(f"LLM Raw Output: {content}")
      
      # Clean possible markdown formatting
      if content.startswith("```json"):
        content = content[7:]
      elif content.startswith("```"):
        content = content[3:]
      if content.endswith("```"):
        content = content[:-3]
      
      content = content.strip()
      
      if not content or content == "{}":
        logger.info("No search criteria identified.")
        return {"output": "I couldn't identify specific criteria to search for. Please specify brand, color, or price."}

      filters = json.loads(content)
      logger.info(f"Extracted filters: {filters}")
      
      # Call the tool directly
      search_result = self.tool.run(filters)
      logger.debug(f"Search Tool Result: {search_result[:200]}...")
      
      # Optional: Allow LLM to summarize, but for now returning raw result string is robust
      # Or we can summarize it:
      if "No products found" in search_result:
        return {"output": search_result}
          
      summary_prompt = f"""
      The user searched for: {user_input}
      The search tool returned: {search_result[:2000]}... (truncated)

      Please summarize these results for the user in a friendly way. Mention the top matches.
      """
      summary_res = self.llm.invoke([HumanMessage(content=summary_prompt)])
      return {"output": summary_res.content}

    except Exception as e:
      logger.error(f"Error in SearchAgent: {e}", exc_info=True)
      return {"output": f"I encountered an error processing your request: {str(e)}"}

