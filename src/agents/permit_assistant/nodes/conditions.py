"""Condition functions for graph routing"""

from ..types import AgentState

def should_continue_after_tools(state: AgentState):
    """Check if we should continue to chatbot or end after tools"""
    if state.get("ui_handled", False):
        print("🔧 DEBUG: UI was handled, ending conversation")
        return "__end__"
    else:
        print("🔧 DEBUG: No UI handled, continuing to chatbot")
        return "chatbot" 