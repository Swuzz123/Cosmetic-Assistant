from typing import TypedDict, Annotated, List
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class SqlAgentState(TypedDict):
    """
    State for the SQL Agent.
    """
    # 'messages' will automatically append new messages due to the `add_messages` reducer
    messages: Annotated[List[BaseMessage], add_messages]
