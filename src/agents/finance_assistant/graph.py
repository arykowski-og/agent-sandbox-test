"""Main graph construction for the finance assistant"""

import asyncio
from langgraph.graph import StateGraph
from langgraph.prebuilt import tools_condition

# Use absolute imports for LangGraph compatibility
from src.agents.finance_assistant.types import FinanceState
from src.agents.finance_assistant.nodes import chatbot_node, tool_node
from src.agents.finance_assistant.tools import get_finance_tools

async def create_finance_agent():
    """Create the finance assistant agent with dual-model approach and MCP tools"""
    finance_tools = await get_finance_tools()
    
    print(f"🛠️ DEBUG: Total tools loaded: {len(finance_tools)}")
    for tool in finance_tools:
        if hasattr(tool, 'name'):
            print(f"   - {tool.name}")
        else:
            print(f"   - {type(tool).__name__}")
    
    print(f"🛠️ DEBUG: Creating dual-model finance graph...")
    
    # Create wrapper functions that pass tools to nodes
    async def chatbot_wrapper(state: FinanceState):
        return await chatbot_node(state, finance_tools)
    
    async def tool_wrapper(state: FinanceState):
        return await tool_node(state, finance_tools)
    
    # Create the StateGraph
    workflow = StateGraph(FinanceState)
    
    # Add nodes
    workflow.add_node("chatbot", chatbot_wrapper)
    workflow.add_node("tools", tool_wrapper)
    
    # Add edges
    workflow.add_edge("__start__", "chatbot")
    
    # Add conditional edges from chatbot
    workflow.add_conditional_edges(
        "chatbot",
        tools_condition,
        {
            "tools": "tools",
            "__end__": "__end__"
        }
    )
    
    # After tools, go back to chatbot for analysis
    workflow.add_edge("tools", "chatbot")
    
    compiled_graph = workflow.compile()
    print(f"🛠️ DEBUG: Graph compiled successfully with nodes: {list(compiled_graph.get_graph().nodes.keys())}")
    print("🏦 Dual-model finance assistant created successfully!")
    print("   - Chatbot Node: gpt-4o (conversation & tool decisions)")
    print("   - Tools Node: o4-mini-2025-04-16 (GraphQL execution)")
    
    return compiled_graph

# For LangGraph compatibility - create graph lazily
def _create_graph_sync():
    """Create graph synchronously for LangGraph"""
    try:
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(create_finance_agent())
    except RuntimeError:
        # No event loop running
        return asyncio.run(create_finance_agent())

# Module-level graph - will be created when first accessed
graph = None

def get_graph():
    """Get the finance assistant graph, creating it if necessary"""
    global graph
    if graph is None:
        graph = _create_graph_sync()
    return graph

# For LangGraph compatibility, set graph at module level
try:
    # Only create if we're not in an async context
    loop = asyncio.get_event_loop()
    if not loop.is_running():
        graph = _create_graph_sync()
except RuntimeError:
    # No event loop, safe to create
    graph = _create_graph_sync()
except Exception:
    # Any other error, defer creation
    pass

if __name__ == "__main__":
    # For testing the agent locally
    print("🏦 Finance Assistant with OpenGov FIN API is ready!")
    print("=" * 60)
    print("Features enabled:")
    print("  ✅ OpenGov FIN GraphQL API integration")
    print("  ✅ Financial data analysis and reporting")
    print("  ✅ Budget and expenditure tracking")
    print("  ✅ Revenue analysis and forecasting")
    print("  ✅ Dual-model approach for optimal performance")
    print("  ✅ Conversation memory and persistence")
    print()
    print("🤖 Chat model: gpt-4o")
    print("🔧 Tool model: o4-mini-2025-04-16")
    print()
    print("Use 'langgraph dev' to start the development server")
    print("Access via agent-chat-ui with assistant=finance_assistant") 