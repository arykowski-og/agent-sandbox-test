"""Chatbot node for the permit assistant"""

from langchain_core.messages import SystemMessage
from src.agents.permit_assistant.config import PERMIT_PROMPT
from src.agents.permit_assistant.types import AgentState

async def chatbot_node(state: AgentState, tools, model):
    """Handle LLM calls with system prompt injection"""
    print(f"🤖 DEBUG: chatbot_node called with {len(state['messages'])} messages")
    
    # Create LLM with tools bound
    llm_with_tools = model.bind_tools(tools)
    
    # Add system prompt if this is the first message or if no system message exists
    messages = state["messages"]
    if not messages or not any(hasattr(msg, 'type') and msg.type == 'system' for msg in messages):
        messages = [SystemMessage(content=PERMIT_PROMPT)] + list(messages)
    
    response = await llm_with_tools.ainvoke(messages)
    
    # Check if the response contains tool calls
    if hasattr(response, 'tool_calls') and response.tool_calls:
        print(f"🤖 DEBUG: LLM wants to call tools: {[tc.get('name', 'unknown') for tc in response.tool_calls]}")
        # Just return the response with tool calls, tools will be executed next
        return {"messages": [response]}
    else:
        print(f"🤖 DEBUG: LLM response without tool calls")
        # This is a regular AI response, no tools called
        return {"messages": [response]} 