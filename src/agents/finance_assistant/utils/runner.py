"""Runner utility for the finance assistant"""

import asyncio
from langchain_core.messages import HumanMessage
from ..graph import create_finance_agent

# Global agent instance
_finance_agent = None

async def get_finance_agent():
    """Get or create the finance assistant agent"""
    global _finance_agent
    if _finance_agent is None:
        _finance_agent = await create_finance_agent()
    return _finance_agent

# Alias for backward compatibility
get_finance_assistant = get_finance_agent

async def run_finance_assistant(message: str) -> str:
    """Run the finance assistant with a user message"""
    try:
        agent = await get_finance_agent()
        result = await agent.ainvoke({"messages": [HumanMessage(content=message)]})
        
        # Get the last message from the result
        messages = result.get("messages", [])
        if messages:
            last_message = messages[-1]
            if hasattr(last_message, 'content'):
                return last_message.content
            else:
                return str(last_message)
        else:
            return "No response generated"
    except Exception as e:
        return f"Error: {str(e)}" 