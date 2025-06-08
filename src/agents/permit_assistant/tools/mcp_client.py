"""MCP client for OpenGov Permitting & Licensing tools"""

import os
from langchain_mcp_adapters.client import MultiServerMCPClient
from src.agents.permit_assistant.config import get_settings

async def get_permit_tools():
    """Get tools from the OpenGov Permitting & Licensing MCP server"""
    try:
        settings = get_settings()
        
        # Configure MCP client with OpenGov PLC server
        client = MultiServerMCPClient({
            "opengov_plc": {
                "command": "python3",
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