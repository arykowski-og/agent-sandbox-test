"""Tools with UI node for handling tool execution and UI emission"""

import uuid
import json
from langgraph.prebuilt import ToolNode
from langgraph.graph.ui import push_ui_message
from langchain_core.messages import AIMessage
from ..types import AgentState
from ..utils import process_records_for_ui

async def tools_with_ui_node(state: AgentState, tools):
    """Execute tools and emit UI components for specific tools"""
    print(f"🔧 DEBUG: tools_with_ui_node called with {len(state['messages'])} messages")
    
    # Store the original messages to access tool calls
    original_messages = state["messages"]
    
    # Execute the tools first
    tool_node = ToolNode(tools=tools)
    tool_result = await tool_node.ainvoke(state)
    
    print(f"🔧 DEBUG: Tool execution completed, now have {len(tool_result['messages'])} messages")
    print(f"🔧 DEBUG: Original messages: {len(original_messages)}")
    
    # Look for get_records tool calls in the original messages
    found_get_records = False
    
    # Check the last message in original_messages for tool calls
    if original_messages:
        last_message = original_messages[-1]
        print(f"🔧 DEBUG: Last original message type: {type(last_message).__name__}, has_tool_calls: {hasattr(last_message, 'tool_calls')}")
        
        if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
            print(f"🔧 DEBUG: Found tool calls in original message: {[tc.get('name', 'unknown') for tc in last_message.tool_calls]}")
            
            for tool_call in last_message.tool_calls:
                if tool_call['name'] == 'get_records':
                    found_get_records = True
                    print(f"🔧 DEBUG: Found get_records tool call with args: {tool_call.get('args', {})}")
                    
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
                                    records = parsed_result["data"]
                                    included_data = parsed_result.get("included", [])
                                    print(f"🔧 DEBUG: Found {len(records)} records in 'data' key")
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
                                
                                # Process records for UI display
                                processed_records = process_records_for_ui(records, included_data)
                                
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
    
    if not found_get_records:
        print(f"🔧 DEBUG: No get_records tool calls found in original messages")
    
    return tool_result 