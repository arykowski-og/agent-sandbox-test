"""MCP client for loading OpenGov tools"""

from langchain_mcp_adapters.client import MultiServerMCPClient
from ..config import get_settings

async def get_permit_tools():
    """Get tools from the OpenGov Permitting & Licensing MCP server"""
    try:
        settings = get_settings()
        
        # Configure MCP client with OpenGov PLC server
        client = MultiServerMCPClient({
            "opengov_plc": {
                "command": "python",
                "args": [settings.mcp_server_path],
                "transport": "stdio",
            }
        })
        
        # Get tools from the MCP server
        tools = await client.get_tools()
        print(f"✅ Loaded {len(tools)} tools from OpenGov PLC MCP server")
        return tools
    except Exception as e:
        print(f"❌ Failed to load MCP tools: {e}")
        return [] 