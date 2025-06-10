"""Tools with UI node for handling tool execution and UI emission"""

import uuid
import json
import asyncio
from typing import Dict, Any, List
from langgraph.prebuilt import ToolNode
from langgraph.graph.ui import push_ui_message
from langchain_core.messages import AIMessage, ToolMessage
from src.agents.permit_assistant.types import AgentState
from src.agents.permit_assistant.utils import process_records_for_ui, get_address_info, get_applicant_name, format_date, get_record_type_name
from src.agents.permit_assistant.utils.schema_generator import generate_record_detail_schema, generate_records_table_schema

async def fetch_related_resource(tools, community: str, relationship_link: str, relationship_name: str):
    """Fetch related resource data from a relationship link"""
    try:
        print(f"🔗 DEBUG: Fetching related resource for {relationship_name}: {relationship_link}")
        
        # Map relationship names to appropriate tool functions (applicant, location, and record type)
        tool_mapping = {
            'applicant': 'get_record_applicant',
            'primaryLocation': 'get_record_primary_location',
            'recordType': 'get_record_type'
        }
        
        # Extract record_id from the relationship link
        record_id = None
        type_id = None
        
        # Handle different URL patterns
        if '/records/' in relationship_link:
            # Pattern: /records/{id}/relationship
            parts = relationship_link.split('/records/')
            if len(parts) > 1:
                record_parts = parts[1].split('/')
                if len(record_parts) > 0:
                    record_id = record_parts[0]
        elif '/recordTypes/' in relationship_link:
            # Pattern: /recordTypes/{id}
            parts = relationship_link.split('/recordTypes/')
            if len(parts) > 1:
                type_parts = parts[1].split('/')
                if len(type_parts) > 0:
                    type_id = type_parts[0]
        else:
            print(f"🔗 DEBUG: Unsupported link pattern: {relationship_link}")
            return None
        
        # Get the appropriate tool name
        tool_name = tool_mapping.get(relationship_name)
        if not tool_name:
            print(f"🔗 DEBUG: No tool mapping found for relationship: {relationship_name}")
            return None
            
        # Find the tool in the available tools (use existing tools instead of creating new MCP connection)
        target_tool = None
        for tool in tools:
            if hasattr(tool, 'name') and tool.name == tool_name:
                target_tool = tool
                break
        
        if not target_tool:
            print(f"🔗 DEBUG: Tool {tool_name} not found in available tools")
            return None
            
        # Check if we have the required ID for the tool
        if tool_name == 'get_record_type' and not type_id:
            print(f"🔗 DEBUG: Could not extract type_id from link for {tool_name}: {relationship_link}")
            return None
        elif tool_name != 'get_record_type' and not record_id:
            print(f"🔗 DEBUG: Could not extract record_id from link for {tool_name}: {relationship_link}")
            return None
            
        # Call the tool with appropriate parameters using the existing tool instance
        if tool_name == 'get_record_type':
            print(f"🔗 DEBUG: Calling {tool_name} with community={community}, record_type_id={type_id}")
            result = await target_tool.ainvoke({"community": community, "record_type_id": type_id})
        else:
            print(f"🔗 DEBUG: Calling {tool_name} with community={community}, record_id={record_id}")
            result = await target_tool.ainvoke({"community": community, "record_id": record_id})
        
        print(f"🔗 DEBUG: Tool {tool_name} returned: {type(result)}")
        
        # Parse the result if it's a string
        if isinstance(result, str):
            try:
                result = json.loads(result)
                print(f"🔗 DEBUG: Parsed tool result as JSON")
            except json.JSONDecodeError:
                print(f"🔗 DEBUG: Tool result is not JSON, using as-is")
        
        return result
        
    except Exception as e:
        print(f"🔗 ERROR: Failed to fetch related resource {relationship_name}: {e}")
        import traceback
        traceback.print_exc()
        return None

async def enhance_records_with_relationships(records, tools, community: str):
    """Enhance records by fetching related resource data for key relationships"""
    if not records:
        return records
        
    # Limit to first 5 records to avoid too many MCP server starts
    limited_records = records[:5]
    print(f"🔗 DEBUG: Enhancing {len(limited_records)} records (limited from {len(records)}) with applicant, address, and record type data")
    print(f"🔗 DEBUG: Available tools: {[getattr(tool, 'name', 'unknown') for tool in tools]}")
    enhanced_records = []
    total_api_calls = 0
    
    # Process all records concurrently
    async def enhance_single_record(record, record_index):
        nonlocal total_api_calls
        enhanced_record = record.copy()
        relationships = record.get("relationships", {})
        
        if not relationships:
            return enhanced_record
            
        print(f"🔗 DEBUG: Record {record.get('id')} has relationships: {list(relationships.keys())}")
        
        # Track enhanced relationship data
        enhanced_relationships = {}
        
        # Only process applicant, primaryLocation, and recordType relationships
        priority_relationships = ['applicant', 'primaryLocation', 'recordType']
        
        # Collect all relationship fetch tasks
        fetch_tasks = []
        relationship_names = []
        
        for rel_name, rel_data in relationships.items():
            if not isinstance(rel_data, dict):
                enhanced_relationships[rel_name] = rel_data
                continue
                
            # Only enhance priority relationships
            if rel_name in priority_relationships and "links" in rel_data and "related" in rel_data["links"]:
                related_link = rel_data["links"]["related"]
                print(f"🔗 DEBUG: Found related link for {rel_name}: {related_link}")
                
                # Add to concurrent fetch tasks
                if related_link and related_link != "/path/to/resource":
                    print(f"🔗 DEBUG: Queuing {rel_name} relationship for record {record_index+1}")
                    fetch_tasks.append(fetch_related_resource(tools, community, related_link, rel_name))
                    relationship_names.append((rel_name, rel_data))
                else:
                    enhanced_relationships[rel_name] = rel_data
            else:
                enhanced_relationships[rel_name] = rel_data
        
        # Execute all relationship fetches concurrently
        if fetch_tasks:
            print(f"🔗 DEBUG: Executing {len(fetch_tasks)} relationship fetches concurrently for record {record_index+1}")
            related_resources = await asyncio.gather(*fetch_tasks, return_exceptions=True)
            total_api_calls += len(fetch_tasks)
            
            # Process the results
            for (rel_name, rel_data), related_resource in zip(relationship_names, related_resources):
                if isinstance(related_resource, Exception):
                    print(f"🔗 ERROR: Failed to fetch {rel_name}: {related_resource}")
                    enhanced_relationships[rel_name] = rel_data
                    continue
                    
                if related_resource:
                    # Extract useful data from the related resource
                    enhanced_rel_data = rel_data.copy()
                    
                    # Parse the result based on the relationship type
                    if rel_name == 'applicant' and isinstance(related_resource, dict):
                        print(f"🔗 DEBUG: Processing applicant resource: {list(related_resource.keys())}")
                        if "data" in related_resource:
                            applicant_data = related_resource["data"]
                            if "attributes" in applicant_data:
                                attrs = applicant_data["attributes"]
                                print(f"🔗 DEBUG: Applicant attributes: {list(attrs.keys())}")
                                # Build applicant name
                                name_parts = []
                                if attrs.get("firstName"):
                                    name_parts.append(attrs["firstName"])
                                if attrs.get("lastName"):
                                    name_parts.append(attrs["lastName"])
                                
                                resolved_name = " ".join(name_parts) if name_parts else attrs.get("email", f"User {applicant_data.get('id')}")
                                enhanced_rel_data["resolved_name"] = resolved_name
                                enhanced_rel_data["resolved_data"] = applicant_data
                                print(f"🔗 DEBUG: Set resolved_name for applicant: '{resolved_name}'")
                        elif isinstance(related_resource, dict) and related_resource.get("error"):
                            print(f"🔗 DEBUG: Applicant resource returned error: {related_resource.get('error')}")
                    
                    elif rel_name == 'primaryLocation' and isinstance(related_resource, dict):
                        print(f"🔗 DEBUG: Processing location resource: {list(related_resource.keys())}")
                        if "data" in related_resource:
                            location_data = related_resource["data"]
                            if "attributes" in location_data:
                                attrs = location_data["attributes"]
                                print(f"🔗 DEBUG: Location attributes: {list(attrs.keys())}")
                                # Build address
                                address_parts = []
                                if attrs.get("streetNumber"):
                                    address_parts.append(str(attrs["streetNumber"]))
                                if attrs.get("streetName"):
                                    address_parts.append(attrs["streetName"])
                                if attrs.get("city"):
                                    address_parts.append(attrs["city"])
                                if attrs.get("state"):
                                    address_parts.append(attrs["state"])
                                if attrs.get("zipCode"):
                                    address_parts.append(attrs["zipCode"])
                                
                                resolved_address = ", ".join(address_parts) if address_parts else f"Location {location_data.get('id')}"
                                enhanced_rel_data["resolved_address"] = resolved_address
                                enhanced_rel_data["resolved_data"] = location_data
                                print(f"🔗 DEBUG: Set resolved_address for location: '{resolved_address}'")
                        elif isinstance(related_resource, dict) and related_resource.get("error"):
                            print(f"🔗 DEBUG: Location resource returned error: {related_resource.get('error')}")
                    
                    elif rel_name == 'recordType' and isinstance(related_resource, dict):
                        print(f"🔗 DEBUG: Processing record type resource: {list(related_resource.keys())}")
                        if "data" in related_resource:
                            type_data = related_resource["data"]
                            if "attributes" in type_data:
                                attrs = type_data["attributes"]
                                print(f"🔗 DEBUG: Record type attributes: {list(attrs.keys())}")
                                resolved_name = attrs.get("name", attrs.get("description", f"Type {type_data.get('id')}"))
                                enhanced_rel_data["resolved_name"] = resolved_name
                                enhanced_rel_data["resolved_data"] = type_data
                                print(f"🔗 DEBUG: Set resolved_name for record type: '{resolved_name}'")
                        elif isinstance(related_resource, dict) and related_resource.get("error"):
                            print(f"🔗 DEBUG: Record type resource returned error: {related_resource.get('error')}")
                    
                    enhanced_relationships[rel_name] = enhanced_rel_data
                    print(f"🔗 DEBUG: Enhanced {rel_name} relationship with resolved data")
                else:
                    enhanced_relationships[rel_name] = rel_data
        
        # Update the record with enhanced relationships
        if enhanced_relationships:
            enhanced_record["relationships"] = enhanced_relationships
        
        return enhanced_record
    
    # Process all records concurrently
    print(f"🔗 DEBUG: Processing {len(limited_records)} records concurrently")
    enhanced_records = await asyncio.gather(*[
        enhance_single_record(record, i) for i, record in enumerate(limited_records)
    ])
    
    # Add any remaining unprocessed records
    if len(records) > len(limited_records):
        remaining_records = records[len(limited_records):]
        enhanced_records.extend(remaining_records)
        print(f"🔗 DEBUG: Added {len(remaining_records)} unprocessed records")
    
    print(f"🔗 DEBUG: Enhanced {len(enhanced_records)} records with applicant, address, and record type data")
    print(f"🔗 DEBUG: Total API calls made: {total_api_calls}")
    return enhanced_records

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
                                
                                # Get community from tool call args
                                community = tool_call.get('args', {}).get('community', 'Unknown')
                                
                                # ENHANCE RECORDS WITH RELATIONSHIP DATA
                                print(f"🔗 DEBUG: About to enhance records with relationship data")
                                enhanced_records = await enhance_records_with_relationships(records, tools, community)
                                print(f"🔗 DEBUG: Enhanced {len(enhanced_records)} records")
                                
                                # Handle get_record (single record) vs get_records (multiple records)
                                print(f"🔧 DEBUG: Checking UI condition - tool_name: '{tool_name}', len(enhanced_records): {len(enhanced_records)}")
                                print(f"🔧 DEBUG: Condition check: tool_name == 'get_record': {tool_name == 'get_record'}, len(enhanced_records) == 1: {len(enhanced_records) == 1}")
                                if tool_name == 'get_record' and len(enhanced_records) == 1:
                                    # Single record - use dynamic UI component
                                    record = enhanced_records[0]
                                    
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
                                    print(f"🔧 DEBUG: Using records_table UI - tool_name: '{tool_name}', len(enhanced_records): {len(enhanced_records)}")
                                    
                                    # Process records to ensure proper field mapping for UI
                                    processed_records = []
                                    for record in enhanced_records:
                                        # Flatten the nested structure - extract attributes
                                        attributes = record.get("attributes", {})
                                        relationships = record.get("relationships", {})
                                        
                                        # Debug: Show what enhanced relationships we have
                                        print(f"🔧 DEBUG: Processing record {record.get('id')} with relationships: {list(relationships.keys())}")
                                        for rel_name, rel_data in relationships.items():
                                            if isinstance(rel_data, dict) and "resolved_name" in rel_data:
                                                print(f"🔧 DEBUG: Found resolved_name for {rel_name}: {rel_data['resolved_name']}")
                                            if isinstance(rel_data, dict) and "resolved_address" in rel_data:
                                                print(f"🔧 DEBUG: Found resolved_address for {rel_name}: {rel_data['resolved_address']}")
                                        
                                        # Create a flattened record with proper field mapping for commonFields
                                        processed_record = {
                                            # Use 'id' for internal tracking but map to commonFields structure
                                            "id": record.get("id"),
                                            
                                            # Record Number - from attributes.number (commonFields expects 'recordNumber')
                                            "recordNumber": attributes.get("number"),
                                            
                                            # Record Type - use enhanced relationship data if available
                                            "recordType": get_record_type_name(
                                                attributes.get('typeID'), 
                                                attributes.get('typeDescription', ''),
                                                relationships
                                            ),
                                            
                                            # Status - from attributes.status (commonFields expects 'status')
                                            "status": attributes.get("status"),
                                            
                                            # Date Submitted - format from UTC to local date (commonFields expects 'dateSubmitted')
                                            "dateSubmitted": format_date(attributes.get("submittedAt")),
                                            
                                            # Applicant Name - use enhanced relationship data if available
                                            "applicantName": (
                                                relationships.get("applicant", {}).get("resolved_name") or
                                                get_applicant_name(record, included_data)
                                            ),
                                            
                                            # Address - use enhanced relationship data if available
                                            "address": (
                                                relationships.get("primaryLocation", {}).get("resolved_address") or
                                                get_address_info(record, included_data)
                                            )
                                        }
                                        
                                        # Debug: Show what we extracted
                                        print(f"🔧 DEBUG: Extracted for record {record.get('id')}: applicantName='{processed_record.get('applicantName')}', address='{processed_record.get('address')}'")
                                        
                                        # Remove None values to avoid showing empty columns
                                        processed_record = {k: v for k, v in processed_record.items() if v is not None and v != ""}
                                        
                                        processed_records.append(processed_record)
                                
                                    print(f"🔧 DEBUG: About to emit UI for {len(processed_records)} records, community: {community}")
                                    
                                    # Create AI message for UI association
                                    ui_message = AIMessage(
                                        id=str(uuid.uuid4()),
                                        content=f"I found {len(processed_records)} records for {community}. The interactive table below shows the details with enhanced relationship data:"
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
                                    
                                    print(f"✅ DEBUG: Successfully emitted records_table UI component for {len(processed_records)} records with enhanced relationship data")
                                    
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