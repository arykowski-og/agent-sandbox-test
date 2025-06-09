"""Main graph construction for the finance assistant"""

import asyncio
from langgraph.graph import StateGraph
from langgraph.prebuilt import tools_condition
from .types import FinanceState
from .nodes import chatbot_node, tool_node
from .tools import get_finance_tools

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