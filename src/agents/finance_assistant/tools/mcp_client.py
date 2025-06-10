"""MCP client for loading OpenGov FIN tools"""

from langchain_mcp_adapters.client import MultiServerMCPClient

# Use absolute imports for LangGraph compatibility
from src.agents.finance_assistant.config import get_settings

async def get_finance_tools():
    """Get tools from the OpenGov FIN GraphQL MCP server"""
    try:
        settings = get_settings()
        
        # Configure MCP client with OpenGov FIN server
        client = MultiServerMCPClient({
            "opengov_fin": {
                "command": "python",
                "args": [settings.mcp_server_path],
                "transport": "stdio",
            }
        })
        
        # Get tools from the MCP server
        tools = await client.get_tools()
        print(f"✅ Loaded {len(tools)} tools from OpenGov FIN GraphQL MCP server")
        return tools
    except Exception as e:
        print(f"❌ Failed to load MCP tools: {e}")
        return [] 