"""Settings and configuration for the finance assistant"""

import os
from typing import NamedTuple
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class FinanceSettings(NamedTuple):
    """Configuration settings for the finance assistant"""
    openai_api_key: str
    og_fin_endpoint: str
    og_fin_token: str
    chat_model_name: str = "gpt-4o"
    tool_model_name: str = "o4-mini-2025-04-16"
    chat_temperature: float = 0.7
    tool_temperature: float = 1.0  # o4-mini only supports temperature=1
    mcp_server_path: str = ""

def get_settings() -> FinanceSettings:
    """Get configuration settings from environment variables"""
    
    # Get current directory for MCP server path
    current_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    mcp_server_path = os.path.join(current_dir, "mcp-servers", "opengov_fin_mcp_server.py")
    
    # Get API keys and endpoints
    api_key = os.getenv("OPENAI_API_KEY", "")
    og_fin_endpoint = os.getenv("OG_FIN_GRAPHQL_ENDPOINT", "")
    og_fin_token = os.getenv("OG_FIN_BEARER_TOKEN", "")
    
    # Validate required settings
    if not api_key:
        print("Warning: OPENAI_API_KEY not found in environment variables.")
    
    if not og_fin_endpoint or not og_fin_token:
        print("Warning: OG_FIN_GRAPHQL_ENDPOINT and/or OG_FIN_BEARER_TOKEN not found in environment variables.")
        print("OpenGov FIN GraphQL features will not be available.")
    
    return FinanceSettings(
        openai_api_key=api_key,
        og_fin_endpoint=og_fin_endpoint,
        og_fin_token=og_fin_token,
        mcp_server_path=mcp_server_path
    ) 