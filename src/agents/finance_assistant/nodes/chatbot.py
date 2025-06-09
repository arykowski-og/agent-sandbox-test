"""Chatbot node for the finance assistant"""

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from ..config import FINANCE_CHAT_PROMPT, get_settings
from ..types import FinanceState

# Initialize the chat model
settings = get_settings()
chat_model = ChatOpenAI(
    model=settings.chat_model_name,
    temperature=settings.chat_temperature
)

async def chatbot_node(state: FinanceState, tools):
    """Main chatbot node: Uses gpt-4o for conversational responses and determines if tools are needed"""
    print(f"🤖 DEBUG: chatbot_node called with {len(state['messages'])} messages")
    
    # Create LLM with tools bound
    llm_with_tools = chat_model.bind_tools(tools)
    
    # Add system prompt if this is the first message or if no system message exists
    messages = state["messages"]
    if not messages or not any(hasattr(msg, 'type') and msg.type == 'system' for msg in messages):
        messages = [SystemMessage(content=FINANCE_CHAT_PROMPT)] + list(messages)
    
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