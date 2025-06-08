"""Type definitions for the finance assistant"""

from typing import Annotated, Sequence, TypedDict
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage

class FinanceState(TypedDict):
    """State definition for the finance assistant agent"""
    messages: Annotated[Sequence[BaseMessage], add_messages] 