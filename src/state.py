import operator
from typing import Annotated, List, TypedDict, Union
from langchain_core.messages import BaseMessage

class AgentState(TypedDict):
    """
    Stores state of the Graph
    messages - Holds the message history
    lead_info - A dictionary to store user details (Name, Email, Platform)
    next_step - A flag to guide the graph ("ask_name", "finished")
    """
    messages: Annotated[List[BaseMessage], operator.add]
    lead_info: dict
    next_step: str