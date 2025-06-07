"""Type definitions for the permit assistant"""

from typing import Annotated, Sequence, TypedDict
from langgraph.graph.message import add_messages
from langgraph.graph.ui import ui_message_reducer, AnyUIMessage

class AgentState(TypedDict):
    """State definition for the permit assistant agent"""
    messages: Annotated[Sequence, add_messages]
    ui: Annotated[Sequence[AnyUIMessage], ui_message_reducer]
    ui_handled: bool 