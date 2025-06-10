"""MCP client for OpenGov Permitting & Licensing tools"""

import os
import time
from langchain_mcp_adapters.client import MultiServerMCPClient
from src.agents.permit_assistant.config import get_settings

# Global cache for MCP client and tools
_mcp_client = None
_cached_tools = None
_client_creation_time = None

async def get_mcp_client():
    """Get or create the MCP client (singleton pattern)"""
    global _mcp_client, _client_creation_time
    
    if _mcp_client is None:
        _client_creation_time = time.time()
        print(f"🔧 DEBUG: Creating NEW MCP client connection at {_client_creation_time}...")
        settings = get_settings()
        
        # Configure MCP client with OpenGov PLC server
        _mcp_client = MultiServerMCPClient({
            "opengov_plc": {
                "command": "python3",
                "args": [settings.mcp_server_path],
                "transport": "stdio",
            }
        })
        print(f"🔧 DEBUG: NEW MCP client created with ID {id(_mcp_client)}")
    else:
        print(f"🔧 DEBUG: REUSING existing MCP client (ID: {id(_mcp_client)}, created at: {_client_creation_time})")
    
    return _mcp_client

async def get_permit_tools():
    """Get tools from the OpenGov Permitting & Licensing MCP server (cached)"""
    global _cached_tools
    
    # Return cached tools if available
    if _cached_tools is not None:
        print(f"🔧 DEBUG: Using cached tools ({len(_cached_tools)} tools)")
        return _cached_tools
    
    try:
        print("🔧 DEBUG: Loading tools from MCP server for the first time...")
        client = await get_mcp_client()
        
        # Get tools from the MCP server
        _cached_tools = await client.get_tools()
        print(f"✅ Loaded {len(_cached_tools)} tools from OpenGov PLC MCP server")
        return _cached_tools
    except Exception as e:
        print(f"❌ Failed to load MCP tools: {e}")
        return []

def clear_mcp_cache():
    """Clear the MCP client and tools cache (useful for testing/debugging)"""
    global _mcp_client, _cached_tools
    _mcp_client = None
    _cached_tools = None
    print("🔧 DEBUG: MCP cache cleared") 