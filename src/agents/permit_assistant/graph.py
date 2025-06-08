"""Main graph construction for the permit assistant"""

import asyncio
from langgraph.graph import StateGraph
from langgraph.prebuilt import tools_condition
from langchain_openai import ChatOpenAI

# Use absolute imports for LangGraph compatibility
from src.agents.permit_assistant.types import AgentState
from src.agents.permit_assistant.nodes import chatbot_node, tools_with_ui_node, should_continue_after_tools
from src.agents.permit_assistant.tools import get_permit_tools
from src.agents.permit_assistant.config import get_settings

async def create_permit_agent():
    """Create the permit assistant agent with MCP tools and UI support"""
    # Get configuration settings
    settings = get_settings()
    
    # Initialize the model
    model = ChatOpenAI(
        model=settings.model_name,
        temperature=settings.temperature
    )
    
    # Get tools from MCP server
    original_tools = await get_permit_tools()
    
    print(f"🛠️ DEBUG: Total tools loaded: {len(original_tools)}")
    for tool in original_tools:
        if hasattr(tool, 'name'):
            print(f"   - {tool.name}")
        else:
            print(f"   - {type(tool).__name__}")
    
    print(f"🛠️ DEBUG: Creating graph with UI support...")
    
    # Create wrapper functions that pass tools and model to nodes
    async def chatbot_wrapper(state: AgentState):
        return await chatbot_node(state, original_tools, model)
    
    async def tools_wrapper(state: AgentState):
        return await tools_with_ui_node(state, original_tools)
    
    # Create the StateGraph with UI support
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("chatbot", chatbot_wrapper)
    workflow.add_node("tools", tools_wrapper)
    
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
    
    # After tools, conditionally go back to chatbot or end
    workflow.add_conditional_edges(
        "tools",
        should_continue_after_tools,
        {
            "chatbot": "chatbot",
            "__end__": "__end__"
        }
    )
    
    compiled_graph = workflow.compile()
    print(f"🛠️ DEBUG: Graph compiled successfully with nodes: {list(compiled_graph.get_graph().nodes.keys())}")
    
    return compiled_graph

# For LangGraph compatibility - create graph lazily
def _create_graph_sync():
    """Create graph synchronously for LangGraph"""
    try:
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(create_permit_agent())
    except RuntimeError:
        # No event loop running
        return asyncio.run(create_permit_agent())

# Module-level graph - will be created when first accessed
graph = None

def get_graph():
    """Get the permit assistant graph, creating it if necessary"""
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
    settings = get_settings()
    print("🏢 Permit Assistant with OpenGov Integration is ready!")
    print("=" * 60)
    print("Features enabled:")
    print("  ✅ OpenGov Permitting & Licensing API integration")
    print("  ✅ Comprehensive permit and license management")
    print("  ✅ Inspection scheduling and tracking")
    print("  ✅ Document and workflow management")
    print("  ✅ Payment and fee tracking")
    print("  ✅ Conversation memory and persistence")
    print()
    
    if settings.og_client_id and settings.og_client_secret:
        print("🔑 OpenGov credentials configured successfully")
    else:
        print("⚠️  OpenGov credentials not configured - some features may not work")
    
    print("Use 'langgraph dev' to start the development server")
    print("Access via agent-chat-ui with assistant=permit_assistant") 