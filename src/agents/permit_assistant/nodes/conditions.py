"""Condition functions for graph routing"""

from ..types import AgentState

def should_continue_after_tools(state: AgentState):
    """Check if we should continue to chatbot or end after tools"""
    ui_handled = state.get("ui_handled", False)
    print(f"🔧 DEBUG: should_continue_after_tools called")
    print(f"🔧 DEBUG: ui_handled = {ui_handled}")
    print(f"🔧 DEBUG: state keys = {list(state.keys())}")
    print(f"🔧 DEBUG: messages count = {len(state.get('messages', []))}")
    
    # Always return to chatbot so LLM can provide a text response
    # The LLM should respond whether UI was emitted or not
    print("🔧 DEBUG: Always continuing to chatbot for LLM response")
    return "chatbot" 