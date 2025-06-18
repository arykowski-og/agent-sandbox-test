# OpenGov Permitting & Licensing MCP Server - Persona Analysis

## Overview

This document analyzes the tools in the OpenGov PLC MCP server to categorize them by intended user persona. The goal is to facilitate refactoring into separate MCP servers for different user types.

## Personas

1. **Permitting Agents** - Government employees who manage permits, workflows, and respond to citizen requests
2. **Citizens** - Individuals applying for permits and checking status of their applications

## Tool Categorization

### 🏛️ **PERMITTING AGENTS ONLY**
*Tools that require administrative privileges and workflow management capabilities*

#### Record Management
- `delete_record` - Only agents should be able to delete records
- `update_record_workflow_step` - Workflow management is an agent responsibility

#### Workflow & Process Management
- `update_inspection_step` - Managing inspection configurations
- `create_inspection_event` - Scheduling inspections
- `update_inspection_event` - Modifying inspection schedules
- `create_inspection_result` - Recording inspection outcomes
- `update_inspection_result` - Updating inspection results
- `create_checklist_result` - Creating checklist results during inspections
- `update_checklist_result` - Updating checklist results
- `update_approval_step` - Managing approval workflows
- `update_document_step` - Managing document generation steps
- `update_payment_step` - Managing payment configurations

#### System Administration
- `create_location` - Creating new locations in the system
- `update_location` - Modifying location data
- `create_user` - User account management
- `get_user_flags` - Administrative user information
- `get_location_flags` - Administrative location information

#### Templates & Configuration
- `get_inspection_type_templates` - System configuration data
- `get_inspection_type_template` - Template details
- `get_checklist_templates` - Checklist configuration
- `get_checklist_template` - Individual checklist template
- `get_record_type_workflow` - Understanding internal workflows
- `get_record_type_document_templates` - Document generation templates

#### Financial Management
- `get_ledger_entries` - Financial system management
- `get_ledger_entry` - Individual ledger entry details

#### Advanced User Management
- `get_users` - User directory (privacy concerns for citizens)
- `remove_record_additional_location` - Administrative location management
- `remove_record_guest` - Administrative user management
- `delete_record_step_comment` - Comment moderation
- `delete_record_attachment` - Attachment management
- `delete_file` - File management

### 👤 **CITIZENS ONLY**
*Tools primarily used during the application process*

#### Application Process
- `create_record_change_request` - Requesting changes to submitted applications

### 🤝 **SHARED TOOLS**
*Tools that both personas can use, but with different contexts and permissions*

#### Record Information & Status
- `get_records` - Agents: manage all records; Citizens: view their applications
- `get_record` - Agents: access any record; Citizens: view their own records
- `list_available_record_ids` - Utility function for both
- `create_record` - Agents: create on behalf of citizens; Citizens: self-application

#### Record Details & Forms
- `get_record_form_details` - Both need to view/edit application forms
- `get_record_form_field` - Accessing specific form fields
- `update_record_form_field` - Agents: corrections; Citizens: filling applications
- `get_record_primary_location` - Viewing application location
- `update_record_primary_location` - Agents: corrections; Citizens: during application
- `get_record_additional_locations` - Viewing all application locations
- `add_record_additional_location` - Adding additional project locations

#### Workflow & Progress Tracking
- `get_record_workflow_steps` - Agents: management; Citizens: tracking progress
- `get_record_workflow_step` - Viewing individual step status
- `get_approval_steps` - Agents: management; Citizens: tracking approvals
- `get_approval_step` - Individual approval status
- `get_document_steps` - Document generation status
- `get_document_step` - Individual document step status

#### Inspections
- `get_inspection_steps` - Agents: management; Citizens: understanding requirements
- `get_inspection_step` - Individual inspection details
- `get_inspection_events` - Agents: scheduling; Citizens: viewing appointments
- `get_inspection_event` - Individual inspection event details
- `get_inspection_results` - Agents: management; Citizens: viewing results
- `get_inspection_result` - Individual inspection result
- `get_checklist_results` - Viewing inspection checklist results
- `get_checklist_result` - Individual checklist result

#### Communications
- `get_record_step_comments` - Viewing workflow step communications
- `create_record_step_comment` - Agents: internal notes; Citizens: responses
- `get_record_change_requests` - Viewing change requests
- `get_record_change_request` - Individual change request details

#### People & Access Management
- `get_record_applicant` - Viewing applicant information
- `get_record_guests` - Viewing authorized users
- `add_record_guest` - Agents: adding staff; Citizens: adding representatives
- `get_user` - Basic user profile information
- `update_user` - Profile management

#### Attachments & Documents
- `get_record_attachments` - Viewing application documents
- `get_record_attachment` - Individual attachment details
- `create_record_attachment` - Agents: internal docs; Citizens: required documents
- `update_record_attachment` - Updating attachment metadata
- `get_files` - File system access
- `get_file` - Individual file access
- `create_file` - File upload preparation
- `update_file` - File metadata updates

#### Payments & Fees
- `get_payment_steps` - Understanding payment requirements
- `get_payment_step` - Individual payment step details
- `get_payment_fees` - Fee information
- `get_payment_fee` - Individual fee details
- `get_transactions` - Agents: financial management; Citizens: payment history
- `get_transaction` - Individual transaction details

#### Reference Data
- `get_locations` - Available locations
- `get_location` - Location details
- `get_departments` - Department information
- `get_department` - Individual department details
- `get_record_types` - Available permit types
- `get_record_type` - Permit type details
- `get_record_type_form` - Application form structure
- `get_record_type_attachments` - Required documents
- `get_record_type_fees` - Fee structure
- `get_projects` - Project information
- `get_organization` - Organization details

## Proposed Refactoring Strategy

### 1. **Citizens MCP Server**
Focus on:
- Application submission and management
- Status tracking and progress monitoring
- Document upload and management
- Payment processing
- Communication with permitting office

### 2. **Permitting Agents MCP Server**
Focus on:
- Complete record management
- Workflow and process administration
- Inspection management
- System configuration
- Financial and reporting tools

### 3. **Shared Utilities**
- Authentication and authorization
- Common API client functionality
- Reference data access
- Error handling patterns

## Implementation Considerations

1. **Security**: Each MCP should enforce appropriate permissions based on user roles
2. **Data Filtering**: Shared tools should filter data appropriately (citizens only see their records)
3. **API Efficiency**: Consider consolidating frequently used combinations of tools
4. **User Experience**: Tailor tool descriptions and error messages for each persona
5. **Compliance**: Ensure citizen-facing tools comply with accessibility and transparency requirements

## Next Steps

1. Create separate MCP server files for each persona
2. Implement role-based data filtering in shared tools
3. Add persona-specific error handling and messaging
4. Consider creating simplified, composite tools for common citizen workflows
5. Add comprehensive documentation for each persona's available tools 