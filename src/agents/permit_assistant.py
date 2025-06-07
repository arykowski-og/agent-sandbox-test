import os
import asyncio
from dotenv import load_dotenv
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.graph.ui import ui_message_reducer, push_ui_message, AnyUIMessage
from langgraph.graph import StateGraph, MessagesState
from langgraph.graph.message import add_messages
from langchain_core.messages import AIMessage, ToolMessage
from langchain_core.tools import tool
import uuid
import json
from typing import Annotated, Sequence, TypedDict, Dict, Any

# Define the agent state with UI support
class AgentState(TypedDict):
    messages: Annotated[Sequence, add_messages]
    ui: Annotated[Sequence[AnyUIMessage], ui_message_reducer]

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
model = ChatOpenAI(
    model="gpt-4o",
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

def create_ui_enhanced_get_records_tool(original_get_records_tool):
    """Create an enhanced get_records tool that emits UI components"""
    
    @tool("get_records")
    async def get_records_with_ui(community: str) -> str:
        """Get a list of records from the community and display them in a table format.
        
        Args:
            community: The community/jurisdiction name to get records from
            
        Returns:
            A summary of the records found
        """
        try:
            print(f"🎯 DEBUG: Enhanced get_records_with_ui tool called for community: {community}")
            # Call the original get_records tool with just the community parameter
            result = await original_get_records_tool.ainvoke({"community": community})
            
            print(f"DEBUG: get_records result type: {type(result)}")
            
            # Parse the result if it's a JSON string
            if isinstance(result, str):
                try:
                    import json
                    result = json.loads(result)
                    print(f"DEBUG: Parsed JSON result type: {type(result)}")
                except json.JSONDecodeError as e:
                    print(f"DEBUG: Failed to parse JSON: {e}")
                    return f"Error: Could not parse response from get_records tool"
            
            # Extract records from the result
            records = []
            if isinstance(result, dict):
                if "data" in result:
                    records = result["data"]
                    print(f"DEBUG: Found {len(records)} records in 'data' key")
                elif "records" in result:
                    records = result["records"]
                    print(f"DEBUG: Found {len(records)} records in 'records' key")
                elif "items" in result:
                    records = result["items"]
                    print(f"DEBUG: Found {len(records)} records in 'items' key")
                else:
                    # If the result is a dict but doesn't have expected keys, treat the whole dict as the data
                    print(f"DEBUG: Available keys in result: {list(result.keys())}")
                    records = [result] if result else []
            elif isinstance(result, list):
                records = result
                print(f"DEBUG: Result is a list with {len(records)} items")
            else:
                # If result is a string or other type, try to parse it
                print(f"DEBUG: Unexpected result type: {type(result)}, value: {result}")
                records = []
            
            if records and len(records) > 0:
                # Create an AI message to associate with the UI component
                message = AIMessage(
                    id=str(uuid.uuid4()),
                    content=f"Successfully retrieved {len(records)} records for {community}. The records are displayed in the table below."
                )
                
                # Emit UI component using push_ui_message with message association
                try:
                    push_ui_message(
                        name="records_table", 
                        props={
                            "records": records,
                            "community": community
                        },
                        message=message
                    )
                    print(f"DEBUG: Successfully emitted UI component for {len(records)} records")
                except Exception as ui_error:
                    print(f"DEBUG: UI emission error: {ui_error}")
                
                return f"Successfully retrieved {len(records)} records for {community}. The records are displayed in the table below."
            else:
                return f"No records found for community: {community}"
                
        except Exception as e:
            return f"Error retrieving records for {community}: {str(e)}"
    
    return get_records_with_ui

async def create_permit_agent():
    """Create the permit assistant agent with MCP tools and UI support"""
    original_tools = await get_permit_tools()
    
    # Find the original get_records tool and create enhanced tools
    original_get_records_tool = None
    for tool in original_tools:
        if hasattr(tool, 'name') and tool.name == "get_records":
            original_get_records_tool = tool
            break
    
    # Create enhanced tools list
    enhanced_tools = []
    for tool in original_tools:
        if hasattr(tool, 'name') and tool.name == "get_records" and original_get_records_tool:
            # Create enhanced get_records tool
            enhanced_get_records = create_ui_enhanced_get_records_tool(original_get_records_tool)
            enhanced_tools.append(enhanced_get_records)
            print(f"🔄 DEBUG: Replaced get_records tool with UI-enhanced version")
        else:
            enhanced_tools.append(tool)
    
    print(f"🛠️ DEBUG: Total tools loaded: {len(enhanced_tools)}")
    for tool in enhanced_tools:
        if hasattr(tool, 'name'):
            print(f"   - {tool.name}")
        else:
            print(f"   - {type(tool).__name__}")
    
    # If no get_records tool was found, we'll just use the original tools
    if not original_get_records_tool:
        enhanced_tools = original_tools
    
    # Create a custom agent node that supports UI
    async def agent_node(state: AgentState):
        # Create a react agent with the enhanced tools
        react_agent = create_react_agent(
            model=model,
            tools=enhanced_tools,
            prompt=permit_prompt
        )
        
        # Invoke the react agent
        result = await react_agent.ainvoke({"messages": state["messages"]})
        
        # Return the result with both messages and ui
        return {
            "messages": result["messages"],
            "ui": state.get("ui", [])  # Preserve existing UI messages
        }
    
    # Create the StateGraph with UI support
    workflow = StateGraph(AgentState)
    workflow.add_node("agent", agent_node)
    workflow.add_edge("__start__", "agent")
    
    return workflow.compile()

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