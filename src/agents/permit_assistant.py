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
    ui_handled: bool

# Load environment variables
load_dotenv()

# Get current directory for MCP server path
current_dir = os.path.dirname(os.path.abspath(__file__))
mcp_server_path = os.path.join(os.path.dirname(current_dir), "mcp-servers", "opengov_plc_mcp_server.py")

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

🚨 **IMPORTANT UI Guidelines:**
- When I call get_records or similar data retrieval tools, I will display the results in an interactive UI component, NOT as text tables
- I should NOT format data as markdown tables in my text responses when a UI component will be shown
- Instead, I should provide a brief summary and let the UI component display the detailed data
- My text responses should complement the UI components, not duplicate them

Always be helpful, accurate, and proactive in identifying potential issues or opportunities. When using the tools, I'll explain what I'm checking and why it's relevant to your specific situation."""

# Note: Removed the old UI-enhanced tool functions since we're now handling UI emission 
# directly in the graph nodes following the LangGraph documentation pattern

async def create_permit_agent():
    """Create the permit assistant agent with MCP tools and UI support"""
    original_tools = await get_permit_tools()
    
    print(f"🛠️ DEBUG: Total tools loaded: {len(original_tools)}")
    for tool in original_tools:
        if hasattr(tool, 'name'):
            print(f"   - {tool.name}")
        else:
            print(f"   - {type(tool).__name__}")
    
    print(f"🛠️ DEBUG: Creating graph with UI support...")
    
    # Create the LLM with tools bound
    llm_with_tools = model.bind_tools(original_tools)
    
    # Define the chatbot node that handles both LLM calls and UI emission
    async def chatbot_node(state: AgentState):
        print(f"🤖 DEBUG: chatbot_node called with {len(state['messages'])} messages")
        
        # Add system prompt if this is the first message or if no system message exists
        messages = state["messages"]
        if not messages or not any(hasattr(msg, 'type') and msg.type == 'system' for msg in messages):
            from langchain_core.messages import SystemMessage
            messages = [SystemMessage(content=permit_prompt)] + list(messages)
        
        response = await llm_with_tools.ainvoke(messages)
        
        # Check if the response contains tool calls
        if hasattr(response, 'tool_calls') and response.tool_calls:
            print(f"🤖 DEBUG: LLM wants to call tools: {[tc.get('name', 'unknown') for tc in response.tool_calls]}")
            # Just return the response with tool calls, tools will be executed next
            return {"messages": [response]}
        else:
            print(f"🤖 DEBUG: LLM response without tool calls")
            # This is a regular AI response, no tools called
            return {"messages": [response]}
    
    # Custom tool node that handles UI emission after tool execution
    async def tools_with_ui_node(state: AgentState):
        """Execute tools and emit UI components for specific tools"""
        from langgraph.prebuilt import ToolNode
        
        print(f"🔧 DEBUG: tools_with_ui_node called with {len(state['messages'])} messages")
        
        # Store the original messages to access tool calls
        original_messages = state["messages"]
        
        # Execute the tools first
        tool_node = ToolNode(tools=original_tools)
        tool_result = await tool_node.ainvoke(state)
        
        print(f"🔧 DEBUG: Tool execution completed, now have {len(tool_result['messages'])} messages")
        print(f"🔧 DEBUG: Original messages: {len(original_messages)}")
        
        # Look for get_records and get_record tool calls in the original messages
        found_ui_tool = False
        
        # Check the last message in original_messages for tool calls
        if original_messages:
            last_message = original_messages[-1]
            print(f"🔧 DEBUG: Last original message type: {type(last_message).__name__}, has_tool_calls: {hasattr(last_message, 'tool_calls')}")
            
            if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
                print(f"🔧 DEBUG: Found tool calls in original message: {[tc.get('name', 'unknown') for tc in last_message.tool_calls]}")
                
                for tool_call in last_message.tool_calls:
                    if tool_call['name'] in ['get_records', 'get_record']:
                        found_ui_tool = True
                        tool_name = tool_call['name']
                        print(f"🔧 DEBUG: Found {tool_name} tool call with args: {tool_call.get('args', {})}")
                        
                        # Find the corresponding tool response in the tool_result
                        tool_response = None
                        for message in tool_result["messages"]:
                            if (hasattr(message, 'tool_call_id') and 
                                message.tool_call_id == tool_call['id']):
                                tool_response = message
                                print(f"🔧 DEBUG: Found matching tool response")
                                break
                        
                        if tool_response:
                            try:
                                print(f"🔧 DEBUG: Processing tool response content type: {type(tool_response.content)}")
                                print(f"🔧 DEBUG: Tool response content preview: {str(tool_response.content)[:200]}...")
                                
                                # Parse the tool response to extract records
                                result = tool_response.content
                                if isinstance(result, str):
                                    try:
                                        import json
                                        parsed_result = json.loads(result)
                                        print(f"🔧 DEBUG: Parsed JSON result with keys: {list(parsed_result.keys()) if isinstance(parsed_result, dict) else 'not a dict'}")
                                    except json.JSONDecodeError as e:
                                        print(f"🔧 DEBUG: JSON decode error: {e}")
                                        continue
                                else:
                                    parsed_result = result
                                    print(f"🔧 DEBUG: Result is not string, type: {type(parsed_result)}")
                                
                                # Extract records and included data from the result
                                records = []
                                included_data = []
                                if isinstance(parsed_result, dict):
                                    if "data" in parsed_result:
                                        data = parsed_result["data"]
                                        # Handle both single record (get_record) and array of records (get_records)
                                        if isinstance(data, list):
                                            records = data
                                        else:
                                            # Single record - wrap in array for consistent processing
                                            records = [data]
                                        included_data = parsed_result.get("included", [])
                                        print(f"🔧 DEBUG: Found {len(records)} records in 'data' key (single record: {not isinstance(data, list)})")
                                        print(f"🔧 DEBUG: Found {len(included_data)} included items")
                                        
                                        # Debug: Show what types of included data we have
                                        if included_data:
                                            included_types = [item.get("type", "unknown") for item in included_data]
                                            print(f"🔧 DEBUG: Included data types: {included_types}")
                                            for i, item in enumerate(included_data[:3]):  # Show first 3 items
                                                print(f"🔧 DEBUG: Included item {i}: type={item.get('type')}, id={item.get('id')}, attributes_keys={list(item.get('attributes', {}).keys())}")
                                        
                                    elif "records" in parsed_result:
                                        records = parsed_result["records"]
                                        included_data = parsed_result.get("included", [])
                                        print(f"🔧 DEBUG: Found {len(records)} records in 'records' key")
                                    elif "items" in parsed_result:
                                        records = parsed_result["items"]
                                        included_data = parsed_result.get("included", [])
                                        print(f"🔧 DEBUG: Found {len(records)} records in 'items' key")
                                    else:
                                        print(f"🔧 DEBUG: No expected keys found, available keys: {list(parsed_result.keys())}")
                                elif isinstance(parsed_result, list):
                                    records = parsed_result
                                    print(f"🔧 DEBUG: Result is list with {len(records)} items")
                                
                                if records and len(records) > 0:
                                    print(f"🔧 DEBUG: Processing {len(records)} records for UI emission")
                                    
                                    # Debug: Show what fields are in the first record
                                    if records:
                                        first_record = records[0]
                                        print(f"🔧 DEBUG: First record fields: {list(first_record.keys())}")
                                        print(f"🔧 DEBUG: First record sample: {dict(list(first_record.items())[:5])}")
                                        
                                        # Show relationships structure if it exists
                                        if "relationships" in first_record:
                                            relationships = first_record["relationships"]
                                            print(f"🔧 DEBUG: First record relationships keys: {list(relationships.keys())}")
                                            for rel_key, rel_value in list(relationships.items())[:3]:  # Show first 3 relationships
                                                print(f"🔧 DEBUG: Relationship '{rel_key}': {rel_value}")
                                        
                                        # Show attributes structure if it exists
                                        if "attributes" in first_record:
                                            attributes = first_record["attributes"]
                                            print(f"🔧 DEBUG: First record attributes keys: {list(attributes.keys())}")
                                            print(f"🔧 DEBUG: First record attributes sample: {dict(list(attributes.items())[:5])}")
                                    
                                    # Handle get_record (single record) vs get_records (multiple records)
                                    print(f"🔧 DEBUG: Checking UI condition - tool_name: '{tool_name}', len(records): {len(records)}")
                                    print(f"🔧 DEBUG: Condition check: tool_name == 'get_record': {tool_name == 'get_record'}, len(records) == 1: {len(records) == 1}")
                                    if tool_name == 'get_record' and len(records) == 1:
                                        # Single record - use get_record UI component
                                        record = records[0]
                                        
                                        # Get community from tool call args
                                        community = tool_call.get('args', {}).get('community', 'Unknown')
                                        
                                        print(f"🔧 DEBUG: About to emit get_record UI for single record, community: {community}")
                                        
                                        # Create AI message for UI association
                                        record_number = record.get("attributes", {}).get("number", record.get("id", "Unknown"))
                                        ui_message = AIMessage(
                                            id=str(uuid.uuid4()),
                                            content=f"Here are the details for record #{record_number}:"
                                        )
                                        
                                        # Emit UI component for single record
                                        print(f"🔧 DEBUG: Emitting get_record UI component with name='get_record'")
                                        push_ui_message(
                                            name="get_record",
                                            props={
                                                "record": record,
                                                "community": community
                                            },
                                            message=ui_message
                                        )
                                        
                                        print(f"✅ DEBUG: Successfully emitted get_record UI component for record {record_number}")
                                        
                                        # Add the UI message to the messages
                                        tool_result["messages"].append(ui_message)
                                        
                                        # Mark that we've handled this with UI
                                        tool_result["ui_handled"] = True
                                        
                                    else:
                                        # Multiple records or get_records tool - use records_table UI component
                                        print(f"🔧 DEBUG: Using records_table UI - tool_name: '{tool_name}', len(records): {len(records)}")
                                        # Helper function to format date from UTC to local
                                        def format_date(date_string):
                                            if not date_string:
                                                return None
                                            try:
                                                from datetime import datetime
                                                # Parse the UTC date
                                                utc_date = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
                                                # Format as local date (just date part for readability)
                                                return utc_date.strftime('%Y-%m-%d')
                                            except:
                                                return date_string
                                        
                                        # Helper function to get a better record type name
                                        def get_record_type_name(type_id, type_description):
                                            # Use description if available and not empty
                                            if type_description and type_description.strip():
                                                return type_description.strip()
                                            
                                            # Otherwise, create a more readable name from typeID
                                            if type_id:
                                                # Common permit type mappings (you can expand this based on your data)
                                                type_mappings = {
                                                    '6413': 'Building Permit',
                                                    '6372': 'Business License', 
                                                    '6370': 'Zoning Permit',
                                                    '6229': 'Temporary Permit',
                                                    '53': 'Special Event Permit'
                                                }
                                                return type_mappings.get(str(type_id), f"Permit Type {type_id}")
                                            
                                            return "Unknown Type"
                                        
                                        # Helper function to extract address info from included data or relationships
                                        def get_address_info(record_data, included_data):
                                            try:
                                                relationships = record_data.get("relationships", {})
                                                print(f"🔧 DEBUG: Record {record_data.get('id')} location relationships: {[k for k in relationships.keys() if 'location' in k.lower()]}")
                                                
                                                # Try different relationship keys for location
                                                location_rel = None
                                                location_key = None
                                                for key in ["primaryLocation", "location", "address", "site"]:
                                                    if key in relationships:
                                                        location_rel = relationships[key]
                                                        location_key = key
                                                        print(f"🔧 DEBUG: Found location relationship under key '{key}': {location_rel}")
                                                        break
                                                
                                                if location_rel:
                                                    # Check if it has data with ID (JSON:API format)
                                                    if "data" in location_rel and location_rel["data"]:
                                                        location_data = location_rel["data"]
                                                        if "id" in location_data:
                                                            location_id = location_data["id"]
                                                            location_type = location_data.get("type", "locations")
                                                            print(f"🔧 DEBUG: Looking for location: id={location_id}, type={location_type}")
                                                            
                                                            # Find the location in included data
                                                            for included_item in included_data:
                                                                if (included_item.get("type") == location_type and 
                                                                    included_item.get("id") == location_id):
                                                                    location_attrs = included_item.get("attributes", {})
                                                                    print(f"🔧 DEBUG: Found location data: {list(location_attrs.keys())}")
                                                                    
                                                                    # Build address from available location attributes
                                                                    address_parts = []
                                                                    if location_attrs.get("streetNumber"):
                                                                        address_parts.append(str(location_attrs["streetNumber"]))
                                                                    if location_attrs.get("streetName"):
                                                                        address_parts.append(location_attrs["streetName"])
                                                                    if location_attrs.get("city"):
                                                                        address_parts.append(location_attrs["city"])
                                                                    if location_attrs.get("state"):
                                                                        address_parts.append(location_attrs["state"])
                                                                    if location_attrs.get("zipCode"):
                                                                        address_parts.append(location_attrs["zipCode"])
                                                                    
                                                                    # Also try other common address fields
                                                                    if not address_parts:
                                                                        for addr_field in ["address", "fullAddress", "streetAddress"]:
                                                                            if location_attrs.get(addr_field):
                                                                                return location_attrs[addr_field]
                                                                    
                                                                    if address_parts:
                                                                        return ", ".join(address_parts)
                                                                    
                                                                    return f"Location {location_id}"
                                                            
                                                            # If relationship exists but no included data found
                                                            return f"Location ID: {location_id}"
                                                    
                                                    # Check if it has direct attributes (non-JSON:API format)
                                                    elif "attributes" in location_rel:
                                                        location_attrs = location_rel["attributes"]
                                                        print(f"🔧 DEBUG: Found direct location attributes: {list(location_attrs.keys())}")
                                                        
                                                        # Build address from available location attributes
                                                        address_parts = []
                                                        if location_attrs.get("streetNumber"):
                                                            address_parts.append(str(location_attrs["streetNumber"]))
                                                        if location_attrs.get("streetName"):
                                                            address_parts.append(location_attrs["streetName"])
                                                        if location_attrs.get("city"):
                                                            address_parts.append(location_attrs["city"])
                                                        if location_attrs.get("state"):
                                                            address_parts.append(location_attrs["state"])
                                                        if location_attrs.get("zipCode"):
                                                            address_parts.append(location_attrs["zipCode"])
                                                        
                                                        # Also try other common address fields
                                                        if not address_parts:
                                                            for addr_field in ["address", "fullAddress", "streetAddress"]:
                                                                if location_attrs.get(addr_field):
                                                                    return location_attrs[addr_field]
                                                        
                                                        if address_parts:
                                                            return ", ".join(address_parts)
                                                    
                                                    # Check if it only has links (OpenGov API pattern)
                                                    elif "links" in location_rel:
                                                        print(f"🔧 DEBUG: Location relationship only has links: {location_rel['links']}")
                                                        # For now, return a placeholder indicating location data is available via link
                                                        return "Address (via API)"
                                                    
                                                    # If relationship exists but no usable data, show placeholder
                                                    return f"Address Available ({location_key})"
                                                
                                                return None
                                            except Exception as e:
                                                print(f"🔧 DEBUG: Error getting address info: {e}")
                                                return None
                                        
                                        # Helper function to get applicant name from included data or relationships
                                        def get_applicant_name(record_data, included_data):
                                            try:
                                                relationships = record_data.get("relationships", {})
                                                print(f"🔧 DEBUG: Record {record_data.get('id')} relationships keys: {list(relationships.keys())}")
                                                
                                                # Try different relationship keys for applicant
                                                applicant_rel = None
                                                applicant_key = None
                                                for key in ["applicant", "user", "owner", "primaryContact", "submittedBy"]:
                                                    if key in relationships:
                                                        applicant_rel = relationships[key]
                                                        applicant_key = key
                                                        print(f"🔧 DEBUG: Found applicant relationship under key '{key}': {applicant_rel}")
                                                        break
                                                
                                                if applicant_rel:
                                                    # Check if it has data with ID (JSON:API format)
                                                    if "data" in applicant_rel and applicant_rel["data"]:
                                                        applicant_data = applicant_rel["data"]
                                                        if "id" in applicant_data:
                                                            applicant_id = applicant_data["id"]
                                                            applicant_type = applicant_data.get("type", "users")
                                                            print(f"🔧 DEBUG: Looking for applicant: id={applicant_id}, type={applicant_type}")
                                                            
                                                            # Find the applicant in included data
                                                            for included_item in included_data:
                                                                if (included_item.get("type") == applicant_type and 
                                                                    included_item.get("id") == applicant_id):
                                                                    applicant_attrs = included_item.get("attributes", {})
                                                                    print(f"🔧 DEBUG: Found applicant data: {list(applicant_attrs.keys())}")
                                                                    
                                                                    # Build name from available attributes
                                                                    name_parts = []
                                                                    if applicant_attrs.get("firstName"):
                                                                        name_parts.append(applicant_attrs["firstName"])
                                                                    if applicant_attrs.get("lastName"):
                                                                        name_parts.append(applicant_attrs["lastName"])
                                                                    
                                                                    if name_parts:
                                                                        return " ".join(name_parts)
                                                                    
                                                                    # Fallback to other name fields
                                                                    for name_field in ["name", "displayName", "fullName", "email"]:
                                                                        if applicant_attrs.get(name_field):
                                                                            return applicant_attrs[name_field]
                                                                    
                                                                    return f"User {applicant_id}"
                                                            
                                                            # If relationship exists but no included data found
                                                            return f"Applicant ID: {applicant_id}"
                                                    
                                                    # Check if it has direct attributes (non-JSON:API format)
                                                    elif "attributes" in applicant_rel:
                                                        applicant_attrs = applicant_rel["attributes"]
                                                        print(f"🔧 DEBUG: Found direct applicant attributes: {list(applicant_attrs.keys())}")
                                                        
                                                        # Build name from available attributes
                                                        name_parts = []
                                                        if applicant_attrs.get("firstName"):
                                                            name_parts.append(applicant_attrs["firstName"])
                                                        if applicant_attrs.get("lastName"):
                                                            name_parts.append(applicant_attrs["lastName"])
                                                        
                                                        if name_parts:
                                                            return " ".join(name_parts)
                                                        
                                                        # Fallback to other name fields
                                                        for name_field in ["name", "displayName", "fullName", "email"]:
                                                            if applicant_attrs.get(name_field):
                                                                return applicant_attrs[name_field]
                                                    
                                                    # Check if it only has links (OpenGov API pattern)
                                                    elif "links" in applicant_rel:
                                                        print(f"🔧 DEBUG: Applicant relationship only has links: {applicant_rel['links']}")
                                                        # For now, return a placeholder indicating applicant data is available via link
                                                        return "Applicant (via API)"
                                                    
                                                    # If relationship exists but no usable data, show placeholder
                                                    return f"Applicant Available ({applicant_key})"
                                                
                                                return None
                                            except Exception as e:
                                                print(f"🔧 DEBUG: Error getting applicant name: {e}")
                                                return None
                                        
                                        # Process records to ensure proper field mapping for UI
                                        processed_records = []
                                        for record in records:
                                            # Flatten the nested structure - extract attributes
                                            attributes = record.get("attributes", {})
                                            
                                            # Create a flattened record with proper field mapping for commonFields
                                            processed_record = {
                                                # Use 'id' for internal tracking but map to commonFields structure
                                                "id": record.get("id"),
                                                
                                                # Record Number - from attributes.number (commonFields expects 'recordNumber')
                                                "recordNumber": attributes.get("number"),
                                                
                                                # Record Type - resolve typeID to meaningful name (commonFields expects 'recordType')
                                                "recordType": get_record_type_name(
                                                    attributes.get('typeID'), 
                                                    attributes.get('typeDescription', '')
                                                ),
                                                
                                                # Status - from attributes.status (commonFields expects 'status')
                                                "status": attributes.get("status"),
                                                
                                                # Date Submitted - format from UTC to local date (commonFields expects 'dateSubmitted')
                                                "dateSubmitted": format_date(attributes.get("submittedAt")),
                                                
                                                # Applicant Name - extract from relationships and included data (commonFields expects 'applicantName')
                                                "applicantName": get_applicant_name(record, included_data),
                                                
                                                # Address - extract from relationships and included data (commonFields expects 'address')
                                                "address": get_address_info(record, included_data)
                                            }
                                            
                                            # Remove None values to avoid showing empty columns
                                            processed_record = {k: v for k, v in processed_record.items() if v is not None and v != ""}
                                            
                                            processed_records.append(processed_record)
                                    
                                    # Get community from tool call args
                                    community = tool_call.get('args', {}).get('community', 'Unknown')
                                    
                                    print(f"🔧 DEBUG: About to emit UI for {len(processed_records)} records, community: {community}")
                                    
                                    # Create AI message for UI association
                                    ui_message = AIMessage(
                                        id=str(uuid.uuid4()),
                                        content=f"I found {len(processed_records)} records for {community}. The interactive table below shows the details:"
                                    )
                                    
                                    # Emit UI component associated with the message
                                    push_ui_message(
                                        name="records_table",
                                        props={
                                            "records": processed_records,
                                            "community": community
                                        },
                                        message=ui_message
                                    )
                                    
                                    print(f"✅ DEBUG: Successfully emitted records_table UI component for {len(processed_records)} records")
                                    
                                    # Add the UI message to the messages
                                    tool_result["messages"].append(ui_message)
                                    
                                    # Mark that we've handled this with UI, so we don't need to go back to chatbot
                                    tool_result["ui_handled"] = True
                                else:
                                    print(f"🔧 DEBUG: No records found to display")
                                    
                            except Exception as e:
                                print(f"❌ DEBUG: Error processing get_records for UI: {e}")
                                import traceback
                                print(f"❌ DEBUG: Full traceback: {traceback.format_exc()}")
        
        if not found_ui_tool:
            print(f"🔧 DEBUG: No UI tool calls found in original messages")
        
        return tool_result
    
    # Import the prebuilt components
    from langgraph.prebuilt import tools_condition
    
    # Define a condition to check if UI was handled
    def should_continue_after_tools(state: AgentState):
        """Check if we should continue to chatbot or end after tools"""
        if state.get("ui_handled", False):
            print("🔧 DEBUG: UI was handled, ending conversation")
            return "__end__"
        else:
            print("🔧 DEBUG: No UI handled, continuing to chatbot")
            return "chatbot"
    
    # Create the StateGraph with UI support
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("chatbot", chatbot_node)
    workflow.add_node("tools", tools_with_ui_node)
    
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
    
    # After tools, conditionally go back to chatbot or end
    workflow.add_conditional_edges(
        "tools",
        should_continue_after_tools,
        {
            "chatbot": "chatbot",
            "__end__": "__end__"
        }
    )
    
    compiled_graph = workflow.compile()
    print(f"🛠️ DEBUG: Graph compiled successfully with nodes: {list(compiled_graph.get_graph().nodes.keys())}")
    
    return compiled_graph

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