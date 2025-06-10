"""Tools with UI node for handling tool execution and UI emission"""

import uuid
import json
from langgraph.prebuilt import ToolNode
from langgraph.graph.ui import push_ui_message
from langchain_core.messages import AIMessage
from src.agents.permit_assistant.types import AgentState
from src.agents.permit_assistant.utils import process_records_for_ui, get_address_info, get_applicant_name, format_date, get_record_type_name
from src.agents.permit_assistant.utils.schema_generator import generate_record_detail_schema, generate_records_table_schema

async def tools_with_ui_node(state: AgentState, tools, model=None):
    """Execute tools and emit UI components for specific tools"""
    print(f"🔧 DEBUG: tools_with_ui_node called with {len(state['messages'])} messages")
    if model:
        print(f"🔧 DEBUG: Using tool model: {model.model_name}")
    
    # Store the original messages to access tool calls
    original_messages = state["messages"]
    
    # Execute the tools first
    tool_node = ToolNode(tools=tools)
    tool_result = await tool_node.ainvoke(state)
    
    print(f"🔧 DEBUG: Tool execution completed, now have {len(tool_result['messages'])} messages")
    print(f"🔧 DEBUG: Original messages: {len(original_messages)}")
    
    # Look for get_records and get_record tool calls in the original messages to emit UI
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
                                    # Single record - use dynamic UI component
                                    record = records[0]
                                    
                                    # Get community from tool call args
                                    community = tool_call.get('args', {}).get('community', 'Unknown')
                                    
                                    print(f"🔧 DEBUG: About to emit dynamic get_record UI for single record, community: {community}")
                                    
                                    # Generate dynamic UI schema
                                    try:
                                        ui_schema = generate_record_detail_schema(record, community)
                                        print(f"🔧 DEBUG: Generated UI schema with {len(ui_schema.get('tabs', []))} tabs")
                                        
                                        # Create AI message for UI association
                                        record_number = record.get("attributes", {}).get("number", record.get("id", "Unknown"))
                                        ui_message = AIMessage(
                                            id=str(uuid.uuid4()),
                                            content=f"Here are the details for record #{record_number}:"
                                        )
                                        
                                        # Emit dynamic UI component for single record
                                        print(f"🔧 DEBUG: Emitting dynamic_record_detail UI component")
                                        push_ui_message(
                                            name="dynamic_record_detail",
                                            props={
                                                "schema": ui_schema,
                                                "community": community
                                            },
                                            message=ui_message
                                        )
                                        
                                        print(f"✅ DEBUG: Successfully emitted dynamic_record_detail UI component for record {record_number}")
                                        
                                        # Add the UI message to the messages
                                        tool_result["messages"].append(ui_message)
                                        
                                    except Exception as schema_error:
                                        print(f"❌ DEBUG: Error generating UI schema: {schema_error}")
                                        # Fallback to original UI
                                        record_number = record.get("attributes", {}).get("number", record.get("id", "Unknown"))
                                        ui_message = AIMessage(
                                            id=str(uuid.uuid4()),
                                            content=f"Here are the details for record #{record_number}:"
                                        )
                                        
                                        push_ui_message(
                                            name="get_record",
                                            props={
                                                "record": record,
                                                "community": community
                                            },
                                            message=ui_message
                                        )
                                        
                                        tool_result["messages"].append(ui_message)
                                    
                                else:
                                    # Multiple records or get_records tool - use records_table UI component
                                    print(f"🔧 DEBUG: Using records_table UI - tool_name: '{tool_name}', len(records): {len(records)}")
                                    
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
                            else:
                                print(f"🔧 DEBUG: No records found to display")
                                
                        except Exception as e:
                            print(f"❌ DEBUG: Error processing {tool_name} for UI: {e}")
                            import traceback
                            print(f"❌ DEBUG: Full traceback: {traceback.format_exc()}")
    
    if not found_ui_tool:
        print(f"🔧 DEBUG: No UI tool calls found in original messages")
    
    # Always return tool results and let the chatbot provide a response
    # The LLM will handle both successful results and failures appropriately
    print(f"🔧 DEBUG: Returning tool results, flow will continue to chatbot for LLM response")
    return tool_result 