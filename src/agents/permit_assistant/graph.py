"""Main graph construction for the permit assistant"""

import asyncio
from langgraph.graph import StateGraph
from langgraph.prebuilt import tools_condition
from .types import AgentState
from .nodes import chatbot_node, tools_with_ui_node, should_continue_after_tools
from .tools import get_permit_tools

async def create_permit_agent():
    """Create the permit assistant agent with MCP tools and UI support"""
    original_tools = await get_permit_tools()
    
    print(f"🛠️ DEBUG: Total tools loaded: {len(original_tools)}")
    for tool in original_tools:
        if hasattr(tool, 'name'):
            print(f"   - {tool.name}")
        else:
            print(f"   - {type(tool).__name__}")
    
    print(f"🛠️ DEBUG: Creating graph with UI support...")
    
    # Create wrapper functions that pass tools to nodes
    async def chatbot_wrapper(state: AgentState):
        return await chatbot_node(state, original_tools)
    
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