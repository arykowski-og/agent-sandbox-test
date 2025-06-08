"""Settings and configuration for the permit assistant"""

import os
from typing import NamedTuple
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings(NamedTuple):
    """Configuration settings for the permit assistant"""
    openai_api_key: str
    og_client_id: str
    og_client_secret: str
    model_name: str = "gpt-4o"
    temperature: float = 0.1
    mcp_server_path: str = ""

def get_settings() -> Settings:
    """Get configuration settings from environment variables"""
    
    # Get current directory for MCP server path
    # From src/agents/permit_assistant/config/settings.py, go up 3 levels to get to src/
    current_file_dir = os.path.dirname(os.path.abspath(__file__))  # config/
    permit_assistant_dir = os.path.dirname(current_file_dir)       # permit_assistant/
    agents_dir = os.path.dirname(permit_assistant_dir)             # agents/
    src_dir = os.path.dirname(agents_dir)                          # src/
    mcp_server_path = os.path.join(src_dir, "mcp-servers", "opengov_plc_mcp_server.py")
    
    # Get API keys
    api_key = os.getenv("OPENAI_API_KEY", "")
    og_client_id = os.getenv("OG_PLC_CLIENT_ID", "")
    og_client_secret = os.getenv("OG_PLC_SECRET", "")
    
    # Validate required settings
    if not api_key:
        print("Warning: OPENAI_API_KEY not found in environment variables.")
    
    if not og_client_id or not og_client_secret:
        print("Warning: OG_PLC_CLIENT_ID and/or OG_PLC_SECRET not found in environment variables.")
        print("OpenGov Permitting & Licensing features will not be available.")
    
    return Settings(
        openai_api_key=api_key,
        og_client_id=og_client_id,
        og_client_secret=og_client_secret,
        mcp_server_path=mcp_server_path
    ) 