# OpenGov Permitting & Licensing MCP Server

This MCP (Model Context Protocol) server provides tools to interact with the OpenGov Permitting & Licensing API. It's designed to be compatible with LangGraph agents and includes comprehensive coverage of all API endpoints.

## Features

- **Complete API Coverage**: Tools for all OpenGov PLC API endpoints
- **OAuth2 Authentication**: Automatic token management with refresh
- **LangGraph Compatible**: Works seamlessly with LangGraph agents
- **Dual Transport Support**: stdio (default) and HTTP transports
- **Comprehensive Error Handling**: Meaningful error messages and proper HTTP status handling
- **Type Safety**: Full type annotations for better development experience

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements-opengov.txt
```

### 2. Environment Variables

Set up your OpenGov API credentials:

```bash
export OG_PLC_CLIENT_ID="your_client_id_here"
export OG_PLC_SECRET="your_client_secret_here"
```

Optional configuration:
```bash
export OG_PLC_BASE_URL="https://api.plce.opengov.com/plce-dome"  # Default production URL
```

### 3. Test the MCP Server

Run the server directly to test:

```bash
python opengov_plc_mcp_server.py
```

Or with HTTP transport:
```bash
python opengov_plc_mcp_server.py --http
```

## Usage with LangGraph

### Basic Integration

```python
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent

# Configure MCP client
client = MultiServerMCPClient({
    "opengov_plc": {
        "command": "python",
        "args": ["/absolute/path/to/opengov_plc_mcp_server.py"],
        "transport": "stdio",
    }
})

# Get tools and create agent
tools = await client.get_tools()
agent = create_react_agent("anthropic:claude-3-5-sonnet-latest", tools)

# Use the agent
response = await agent.ainvoke({
    "messages": [{"role": "user", "content": "Get all records for community 'demo'"}]
})
```

### Run Example

```bash
# Update the path in the example file first
python opengov_plc_usage_example.py

# Or run in interactive mode
python opengov_plc_usage_example.py --interactive
```

## Available Tools

The MCP server provides tools for all OpenGov PLC API endpoints, organized by category:

### Records
- `get_records` - List records with filtering
- `get_record` - Get specific record
- `create_record` - Create new record
- `update_record` - Update existing record
- `delete_record` - Delete record

### Record Management
- **Attachments**: `get_record_attachments`, `create_record_attachment`, etc.
- **Workflow Steps**: `get_record_workflow_steps`, `update_record_workflow_step`, etc.
- **Form Fields**: `get_record_form_details`, `update_record_form_field`, etc.
- **Locations**: `get_record_primary_location`, `add_record_additional_location`, etc.
- **Users**: `get_record_applicant`, `add_record_guest`, etc.
- **Change Requests**: `get_record_change_requests`, `create_record_change_request`, etc.

### Locations & Users
- `get_locations`, `create_location`, `update_location`
- `get_users`, `create_user`, `update_user`
- `get_location_flags`, `get_user_flags`

### Configuration
- `get_departments`, `get_record_types`
- `get_record_type_form`, `get_record_type_workflow`
- `get_organization`

### Inspections
- **Steps**: `get_inspection_steps`, `update_inspection_step`
- **Events**: `get_inspection_events`, `create_inspection_event`
- **Results**: `get_inspection_results`, `create_inspection_result`
- **Checklists**: `get_checklist_results`, `create_checklist_result`
- **Templates**: `get_inspection_type_templates`, `get_checklist_templates`

### Workflow Management
- **Approvals**: `get_approval_steps`, `update_approval_step`
- **Documents**: `get_document_steps`, `update_document_step`
- **Payments**: `get_payment_steps`, `get_payment_fees`

### Financial
- `get_transactions`, `get_ledger_entries`

### Files
- `get_files`, `create_file`, `update_file`, `delete_file`

### Projects
- `get_projects`

## Example Queries

Here are some example natural language queries you can use with the LangGraph agent:

1. **Basic Data Retrieval**:
   - "Get all records for the community 'demo'"
   - "Show me the departments in the 'demo' community"
   - "List all record types available"

2. **Record Management**:
   - "Create a new building permit record for community 'demo'"
   - "Get all attachments for record ID '12345'"
   - "Update the status of workflow step '67890'"

3. **Inspections**:
   - "List all inspection events for community 'demo'"
   - "Create a new inspection result for inspection '11111'"
   - "Get all checklist templates"

4. **Users and Locations**:
   - "Find all users in the system"
   - "Get location details for location ID '54321'"
   - "Add a new guest to record '12345'"

5. **Financial**:
   - "Get all payment transactions"
   - "List fees for payment step '99999'"
   - "Show ledger entries"

## Error Handling

The server includes comprehensive error handling:

- **Authentication Errors**: Automatic token refresh and clear error messages
- **API Errors**: HTTP status codes and response details
- **Network Errors**: Connection timeout and retry information
- **Validation Errors**: Parameter validation and format checking

## Development

### Adding New Tools

To add new tools, follow this pattern:

```python
@mcp.tool()
async def new_tool_name(community: str, param1: str, param2: Optional[str] = None) -> Dict:
    """Tool description"""
    params = {}
    if param2:
        params["param2"] = param2
    
    return await client.make_request("GET", f"/new-endpoint/{param1}", community, params=params)
```

### Testing

1. Set up test environment variables
2. Run the server: `python opengov_plc_mcp_server.py`
3. Test with example: `python opengov_plc_usage_example.py`
4. Use interactive mode: `python opengov_plc_usage_example.py --interactive`

## Troubleshooting

### Common Issues

1. **Authentication Failed**
   - Verify `OG_PLC_CLIENT_ID` and `OG_PLC_SECRET` are set correctly
   - Check if credentials have expired
   - Ensure you have proper API access permissions

2. **Community Not Found**
   - Verify the community name exists in your OpenGov instance
   - Check if you have access to the specified community

3. **Tool Loading Errors**
   - Ensure all dependencies are installed: `pip install -r requirements-opengov.txt`
   - Verify the MCP server path is correct in your client configuration

4. **Network Errors**
   - Check your internet connection
   - Verify the base URL is correct (staging vs production)
   - Check if there are firewall restrictions

### Debug Mode

Enable debug logging by setting:
```bash
export PYTHONUNBUFFERED=1
```

## API Documentation

For detailed API documentation, refer to the OpenGov Permitting & Licensing API documentation or the included OpenAPI specification file.

## License

This MCP server is provided as-is for integration with OpenGov Permitting & Licensing systems. Please ensure compliance with your OpenGov API usage terms and conditions. 