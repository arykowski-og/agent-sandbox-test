# Permit Assistant - OpenGov Integration

The Permit Assistant is an AI agent that helps users navigate permitting and licensing processes through the OpenGov Permitting & Licensing system. It provides comprehensive support for municipal permits, licenses, inspections, and compliance tracking.

## Quick Start

### 1. Setup Environment Variables

Add your OpenGov credentials to your `.env` file:

```bash
# OpenGov Permitting & Licensing API credentials
OG_PLC_CLIENT_ID=your_client_id_here
OG_PLC_SECRET=your_client_secret_here

# Optional: Custom base URL (defaults to production)
OG_PLC_BASE_URL=https://api.plce.opengov.com/plce-dome

# Required: OpenAI API key for the agent
OPENAI_API_KEY=your_openai_key_here
```

### 2. Start LangGraph Server

```bash
langgraph dev
```

### 3. Access via Agent Chat UI

Open the agent-chat-ui and use:
```
http://localhost:3000/chat?assistantId=permit_assistant&apiUrl=http://localhost:8123
```

## Features

### 🏢 **Core Capabilities**
- **Records Management**: Search, view, create, and update permit/license records
- **Inspections**: Schedule inspections, view results, track compliance
- **Workflow Tracking**: Monitor approval processes and workflow steps
- **Document Management**: Handle attachments, forms, and required documentation
- **Payment Processing**: Track fees, payments, and financial transactions
- **Location Services**: Manage property locations and address verification
- **User Management**: Handle applicants, guests, and stakeholder information

### 📋 **Common Use Cases**

1. **Permit Status Checks**
   - "What's the status of permit #12345?"
   - "Show me all active building permits for community 'demo'"

2. **Application Guidance**
   - "How do I apply for a building permit?"
   - "What documents do I need for a business license?"

3. **Inspection Management**
   - "Schedule an inspection for permit #12345"
   - "What inspections are due this week?"

4. **Compliance Tracking**
   - "Check compliance status for location ID 98765"
   - "List all overdue permits"

5. **Fee and Payment Information**
   - "What fees are required for this permit type?"
   - "Show payment history for permit #12345"

## Example Queries

### Basic Information
```
"What record types are available in the demo community?"
"Show me the organization information for the demo community"
"List all departments in the system"
```

### Record Management
```
"Get all records for the community 'demo'"
"Show me details for record ID ABC123"
"Create a new building permit for 123 Main St"
```

### Inspections
```
"List all inspection events for community 'demo'"
"What are the inspection requirements for building permits?"
"Show me the checklist for inspection ID 456"
```

### Workflow and Approvals
```
"What's the approval workflow for commercial permits?"
"Show me pending approval steps for record ABC123"
"Update the status of workflow step 789"
```

## Architecture

```
Agent Chat UI → LangGraph Server → Permit Assistant → MCP Server → OpenGov API
```

- **Agent Chat UI**: Web interface for user interaction
- **LangGraph Server**: Hosts the permit assistant agent
- **Permit Assistant**: AI agent with specialized permit knowledge
- **MCP Server**: Provides tools for OpenGov API access
- **OpenGov API**: Backend permitting system

## API Coverage

The permit assistant has access to **70+ tools** covering all OpenGov PLC API endpoints:

### Records & Applications
- CRUD operations for permits and licenses
- Attachments and document management
- Form field management
- Change request tracking

### Workflow Management
- Workflow step tracking and updates
- Comments and collaboration
- Approval processes
- Document generation

### Inspections
- Inspection scheduling and results
- Checklist management
- Template configuration
- Compliance tracking

### Financial
- Fee calculation and tracking
- Payment processing
- Transaction history
- Ledger management

### Administration
- User management
- Location services
- Department configuration
- Organization settings

## Troubleshooting

### Common Issues

1. **"OpenGov credentials not configured"**
   - Ensure `OG_PLC_CLIENT_ID` and `OG_PLC_SECRET` are set in your `.env` file
   - Verify credentials are valid and active

2. **"Failed to load MCP tools"**
   - Check that the MCP server dependencies are installed: `pip install mcp aiohttp`
   - Verify the MCP server path is correct

3. **"API request failed"**
   - Verify the community name exists in your OpenGov instance
   - Check your API permissions
   - Ensure you're using the correct base URL (staging vs production)

4. **Agent not responding**
   - Check that LangGraph server is running: `langgraph dev`
   - Verify the `assistantId=permit_assistant` parameter in the URL
   - Check browser console for errors

### Debug Mode

Enable verbose logging:
```bash
export PYTHONUNBUFFERED=1
langgraph dev --verbose
```

## Development

### Adding Custom Functionality

The permit assistant can be extended by:

1. **Adding new MCP tools** in `src/mcp/opengov_plc_mcp_server.py`
2. **Customizing the agent prompt** in `src/agents/permit_assistant.py`
3. **Adding specialized workflows** for your jurisdiction's requirements

### Testing

Test the individual components:

```bash
# Test MCP server
python src/mcp/opengov_plc_mcp_server.py

# Test permit assistant
python src/agents/permit_assistant.py

# Test with agent chat UI
langgraph dev
# Open http://localhost:3000/chat?assistantId=permit_assistant&apiUrl=http://localhost:8123
```

## Support

For OpenGov API documentation and support, refer to your OpenGov administrator or the official OpenGov documentation portal. 