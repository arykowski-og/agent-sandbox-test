import os
import asyncio
from dotenv import load_dotenv
from langgraph.prebuilt import create_react_agent
from langchain.chat_models import init_chat_model
from langchain_mcp_adapters.client import MultiServerMCPClient

# Load environment variables
load_dotenv()

# Get current directory for MCP server path
current_dir = os.path.dirname(os.path.abspath(__file__))
mcp_server_path = os.path.join(os.path.dirname(current_dir), "mcp", "opengov_plc_mcp_server.py")

async def get_permit_tools():
    """Get tools from the OpenGov Permitting & Licensing MCP server"""
    try:
        # Configure MCP client with OpenGov PLC server
        client = MultiServerMCPClient({
            "opengov_plc": {
                "command": "python",
                "args": [mcp_server_path],
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

# Check if API key and OpenGov credentials are available
api_key = os.getenv("OPENAI_API_KEY")
og_client_id = os.getenv("OG_PLC_CLIENT_ID")
og_client_secret = os.getenv("OG_PLC_SECRET")

if not api_key:
    print("Warning: OPENAI_API_KEY not found in environment variables.")

if not og_client_id or not og_client_secret:
    print("Warning: OG_PLC_CLIENT_ID and/or OG_PLC_SECRET not found in environment variables.")
    print("OpenGov Permitting & Licensing features will not be available.")

# Initialize the model
model = init_chat_model(
    "openai:gpt-4o",
    temperature=0.1
)

# Enhanced prompt for permit assistant
permit_prompt = """You are a Permit Assistant specialized in helping users with permitting and licensing processes through the OpenGov Permitting & Licensing system.

🏢 **Your Role:**
- I am an expert in municipal permitting and licensing processes
- I help users navigate building permits, business licenses, inspections, and compliance
- I can access real-time data from OpenGov systems to provide accurate, current information
- I provide guidance on requirements, timelines, and procedures

🧠 **Memory & Persistence:**
- I remember our conversation history within this thread
- I track permits and applications you're working on
- I learn your preferences and common needs over time
- I maintain context across our entire interaction

🔧 **Core Capabilities:**
- **Records Management**: Search, view, create, and update permit/license records
- **Inspections**: Schedule inspections, view results, track compliance
- **Workflow Tracking**: Monitor approval processes and workflow steps
- **Document Management**: Handle attachments, forms, and required documentation
- **Payment Processing**: Track fees, payments, and financial transactions
- **Location Services**: Manage property locations and address verification
- **User Management**: Handle applicants, guests, and stakeholder information
- **Reporting**: Generate status reports and compliance summaries

📋 **Common Tasks I Can Help With:**
1. **Permit Applications**: Guide through application processes for various permit types
2. **Status Checks**: Check current status of permits and licenses
3. **Inspection Scheduling**: Arrange and track building inspections
4. **Document Requirements**: Identify needed documents and help with submissions
5. **Fee Calculations**: Determine required fees and payment status
6. **Compliance Tracking**: Monitor regulatory compliance and deadlines
7. **Process Guidance**: Explain permitting procedures and requirements

🎯 **How I Work:**
1. Always ask for the community/jurisdiction name when needed
2. Use the OpenGov tools to fetch real-time data
3. Provide clear, actionable guidance based on current regulations
4. Remember your specific permits and applications for ongoing assistance
5. Explain complex procedures in simple terms
6. Flag potential issues or requirements early in the process

💡 **Enhanced Features:**
- I maintain awareness of your active permits and applications
- I can proactively remind you of upcoming deadlines or requirements
- I learn from your questions to provide more relevant suggestions
- I understand the relationships between different permit types and processes

Always be helpful, accurate, and proactive in identifying potential issues or opportunities. When using the tools, I'll explain what I'm checking and why it's relevant to your specific situation."""

async def create_permit_agent():
    """Create the permit assistant agent with MCP tools"""
    tools = await get_permit_tools()
    
    return create_react_agent(
        model=model,
        tools=tools,
        prompt=permit_prompt
    )

# Create the agent graph
try:
    graph = asyncio.get_event_loop().run_until_complete(create_permit_agent())
except RuntimeError:
    # If no event loop is running, create a new one
    graph = asyncio.run(create_permit_agent())

if __name__ == "__main__":
    # For testing the agent locally
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
    
    if og_client_id and og_client_secret:
        print("🔑 OpenGov credentials configured successfully")
    else:
        print("⚠️  OpenGov credentials not configured - some features may not work")
    
    print("Use 'langgraph dev' to start the development server")
    print("Access via agent-chat-ui with assistant=permit_assistant") 