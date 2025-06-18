# OpenGov Permitting & Licensing MCP Servers

This directory contains three versions of the OpenGov Permitting & Licensing MCP server, each tailored for different user personas based on the analysis in `opengov_plc_persona_analysis.md`.

## Server Variants

### 1. `opengov_plc_mcp_server.py` - **Complete Server (Backward Compatibility)**
- **Tools**: 93 tools (all available functions)
- **Purpose**: Original complete server maintained for backward compatibility
- **Users**: Any user with appropriate API credentials
- **Features**: All administrative and citizen-facing tools

### 2. `opengov_plc_app.py` - **Government Agents Server**
- **Tools**: 93 tools (complete administrative access)
- **Purpose**: Designed for government permitting agents and staff
- **Users**: Government employees, permitting agents, administrative staff
- **Features**:
  - Complete record management (create, read, update, delete)
  - Administrative tools (user management, system configuration)
  - Workflow management (inspection scheduling, approval processes)
  - Financial management (ledger entries, payment configuration)
  - System templates and configuration access

### 3. `opengov_plc_portal.py` - **Citizens Portal**
- **Tools**: 68 tools (citizen-focused, security-filtered)
- **Purpose**: Designed for citizens applying for permits and checking status
- **Users**: Citizens, permit applicants, authorized representatives
- **Features**:
  - Application submission and management
  - Status tracking and progress monitoring
  - Document upload and management
  - Payment processing and fee information
  - Communication with permitting office
  - Reference data access (permit types, locations, requirements)

## Security Differences

### Administrative Tools Removed from Citizens Portal
The following 25 administrative tools are **NOT** available in the citizens portal for security reasons:

- `delete_record` - Only agents can delete records
- `update_record_workflow_step` - Workflow management is administrative
- `create/update_inspection_*` - Inspection management is agent-only
- `create/update_location` - Location management is administrative
- `create_user` - User account creation is administrative
- `get_user_flags` / `get_location_flags` - Administrative flags are sensitive
- `get_users` - User directory access restricted for privacy
- Template and configuration tools - System configuration is administrative
- `get_ledger_entries` - Financial records are administrative
- `delete_*` operations - Deletion rights are restricted

### Shared Tools with Different Context
Many tools are available in both servers but serve different purposes:

- **`get_records`**: 
  - Agents: Access to all records for management
  - Citizens: Limited to authorized records (own applications)
- **`create_record`**: 
  - Agents: Create records on behalf of citizens
  - Citizens: Submit new permit applications
- **Workflow tools**: 
  - Agents: Management and administration
  - Citizens: Status tracking and progress monitoring

## Usage

Each server can be run independently:

```bash
# Government Agents Server
python src/mcp-servers/opengov_plc_app.py

# Citizens Portal
python src/mcp-servers/opengov_plc_portal.py

# Original Complete Server (backward compatibility)
python src/mcp-servers/opengov_plc_mcp_server.py
```

## Environment Variables

All servers use the same environment variables:
- `OG_PLC_CLIENT_ID` - OpenGov API client ID
- `OG_PLC_SECRET` - OpenGov API client secret  
- `OG_PLC_BASE_URL` - OpenGov API base URL (optional, defaults to production)

## Implementation Notes

- **Authentication**: All servers use the same OAuth2 client credentials flow
- **API Client**: Shared `OpenGovPLCClient` class across all servers
- **Error Handling**: Consistent error handling and response formatting
- **Documentation**: Tool descriptions updated to reflect intended persona usage
- **Transport**: All servers support both stdio and HTTP transport modes 