"""Chatbot node for the permit assistant"""

from langchain_core.messages import SystemMessage
from src.agents.permit_assistant.config import PERMIT_PROMPT
from src.agents.permit_assistant.types import AgentState
from src.agents.permit_assistant.follow_up_actions import create_follow_up_hook

async def chatbot_node(state: AgentState, tools, model):
    """Handle LLM calls with system prompt injection"""
    print(f"🤖 DEBUG: chatbot_node called with {len(state['messages'])} messages")
    
    # Debug: Show the types and content of recent messages
    if state["messages"]:
        print(f"🤖 DEBUG: Recent message types: {[type(msg).__name__ for msg in state['messages'][-3:]]}")
        for i, msg in enumerate(state["messages"][-3:]):
            msg_preview = str(getattr(msg, 'content', str(msg)))[:100]
            print(f"🤖 DEBUG: Message {len(state['messages'])-3+i}: {type(msg).__name__} - {msg_preview}...")
    
    # Create LLM with tools bound
    llm_with_tools = model.bind_tools(tools)
    
    # Add system prompt if this is the first message or if no system message exists
    messages = state["messages"]
    if not messages or not any(hasattr(msg, 'type') and msg.type == 'system' for msg in messages):
        messages = [SystemMessage(content=PERMIT_PROMPT)] + list(messages)
    
    print(f"🤖 DEBUG: About to call LLM with {len(messages)} messages")
    response = await llm_with_tools.ainvoke(messages)
    print(f"🤖 DEBUG: LLM response received: {type(response).__name__}")
    
    # Check if the response contains tool calls
    if hasattr(response, 'tool_calls') and response.tool_calls:
        print(f"🤖 DEBUG: LLM wants to call tools: {[tc.get('name', 'unknown') for tc in response.tool_calls]}")
        # Just return the response with tool calls, tools will be executed next
        return {"messages": [response]}
    else:
        print(f"🤖 DEBUG: LLM response without tool calls")
        print(f"🤖 DEBUG: Response content preview: {str(getattr(response, 'content', 'No content'))[:200]}...")
        
        # Generate follow-up actions for non-tool responses
        print(f"🤖 DEBUG: Generating follow-up actions...")
        try:
            from src.agents.permit_assistant.follow_up_actions import extract_follow_up_actions_hook
            
            # Create config for the hook
            hook_kwargs = {
                "config": {
                    "llm": model,
                    "configurable": {
                        "messages": state["messages"]
                    }
                }
            }
            
            # Apply the follow-up actions hook
            response_with_actions = await extract_follow_up_actions_hook(response, **hook_kwargs)
            print(f"🤖 DEBUG: Follow-up actions applied")
            
            return {"messages": [response_with_actions]}
            
        except Exception as e:
            print(f"🤖 ERROR: Failed to generate follow-up actions: {e}")
            import traceback
            traceback.print_exc()
            # Return original response if follow-up generation fails
            return {"messages": [response]} 