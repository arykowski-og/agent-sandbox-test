"""
Permit Assistant Agent - Refactored Version

A specialized agent for helping users with permitting and licensing processes
through the OpenGov Permitting & Licensing system.

This is the new refactored version with improved code organization.
"""

import asyncio
from permit_assistant import create_permit_agent
from permit_assistant.config import get_settings

# Create the agent graph
try:
    graph = asyncio.get_event_loop().run_until_complete(create_permit_agent())
except RuntimeError:
    # If no event loop is running, create a new one
    graph = asyncio.run(create_permit_agent())

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
    print("  ✅ Modular, maintainable code structure")
    print()
    
    if settings.og_client_id and settings.og_client_secret:
        print("🔑 OpenGov credentials configured successfully")
    else:
        print("⚠️  OpenGov credentials not configured - some features may not work")
    
    print("Use 'langgraph dev' to start the development server")
    print("Access via agent-chat-ui with assistant=permit_assistant") 