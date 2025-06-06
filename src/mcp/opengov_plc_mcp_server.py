#!/usr/bin/env python3
"""
OpenGov Permitting & Licensing MCP Server

This MCP server provides tools to interact with the OpenGov Permitting & Licensing API.
It supports OAuth2 Client Credentials authentication and provides tools for all API endpoints.
"""

import os
import json
import asyncio
import aiohttp
from typing import Dict, List, Any, Optional, Union
from fastmcp import FastMCP
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize MCP server
mcp = FastMCP("OpenGov Permitting & Licensing")

class OpenGovPLCClient:
    """Client for OpenGov Permitting & Licensing API"""
    
    def __init__(self):
        self.client_id = os.getenv("OG_PLC_CLIENT_ID")
        self.client_secret = os.getenv("OG_PLC_SECRET")
        self.base_url = os.getenv("OG_PLC_BASE_URL", "https://api.plce.opengov.com/plce-dome")
        self.auth_url = "https://accounts.viewpointcloud.com/oauth/token"
        self.access_token = None
        self.token_expires_at = None
        
        if not self.client_id or not self.client_secret:
            raise ValueError("OG_PLC_CLIENT_ID and OG_PLC_SECRET environment variables are required")
    
    async def get_access_token(self) -> str:
        """Get or refresh OAuth2 access token"""
        if self.access_token and self.token_expires_at and datetime.now() < self.token_expires_at:
            return self.access_token
        
        async with aiohttp.ClientSession() as session:
            data = {
                "grant_type": "client_credentials",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "audience": "viewpointcloud.com/api/production"
            }
            
            async with session.post(self.auth_url, data=data) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Failed to get access token: {response.status} - {error_text}")
                
                token_data = await response.json()
                self.access_token = token_data["access_token"]
                expires_in = token_data.get("expires_in", 3600)
                self.token_expires_at = datetime.now() + timedelta(seconds=expires_in - 60)
                
                return self.access_token
    
    async def make_request(self, method: str, endpoint: str, community: str, 
                          params: Optional[Dict] = None, json_data: Optional[Dict] = None) -> Dict:
        """Make authenticated API request"""
        token = await self.get_access_token()
        url = f"{self.base_url}/v2/{community}{endpoint}"
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.request(method, url, headers=headers, params=params, json=json_data) as response:
                if response.status >= 400:
                    error_text = await response.text()
                    raise Exception(f"API request failed with status {response.status}: {error_text}")
                
                return await response.json()

# Global client instance - initialized lazily
client = None

def get_client():
    """Get or create the OpenGov client instance"""
    global client
    if client is None:
        client = OpenGovPLCClient()
    return client

def build_params(**kwargs) -> Optional[Dict]:
    """Build parameters dictionary, excluding None values"""
    params = {}
    for key, value in kwargs.items():
        if value is not None:
            params[key] = value
    return params if params else None

# RECORD TOOLS

@mcp.tool
async def get_records(community: str) -> Dict:
    """Get a list of records from the community
    
    Note: The OpenGov API does not support pagination or filtering parameters for this endpoint.
    All records are returned in a single response.
    """
    return await get_client().make_request("GET", "/records", community)

@mcp.tool
async def get_record(community: str, record_id: str) -> Dict:
    """Get a specific record by ID"""
    return await get_client().make_request("GET", f"/records/{record_id}", community)

@mcp.tool
async def create_record(community: str, record_data: Dict) -> Dict:
    """Create a new record"""
    return await get_client().make_request("POST", "/records", community, json_data=record_data)

@mcp.tool
async def update_record(community: str, record_id: str, record_data: Dict) -> Dict:
    """Update an existing record"""
    return await get_client().make_request("PUT", f"/records/{record_id}", community, json_data=record_data)

@mcp.tool
async def delete_record(community: str, record_id: str) -> Dict:
    """Delete a record"""
    return await get_client().make_request("DELETE", f"/records/{record_id}", community)

# RECORD ATTACHMENTS

@mcp.tool
async def get_record_attachments(community: str, record_id: str) -> Dict:
    """Get attachments for a record"""
    return await get_client().make_request("GET", f"/records/{record_id}/attachments", community)

@mcp.tool
async def get_record_attachment(community: str, record_id: str, attachment_id: str) -> Dict:
    """Get a specific record attachment"""
    return await get_client().make_request("GET", f"/records/{record_id}/attachments/{attachment_id}", community)

@mcp.tool
async def create_record_attachment(community: str, record_id: str, attachment_data: Dict) -> Dict:
    """Create a new record attachment"""
    return await get_client().make_request("POST", f"/records/{record_id}/attachments", community, json_data=attachment_data)

@mcp.tool
async def update_record_attachment(community: str, record_id: str, attachment_id: str, attachment_data: Dict) -> Dict:
    """Update a record attachment"""
    return await get_client().make_request("PUT", f"/records/{record_id}/attachments/{attachment_id}", community, json_data=attachment_data)

@mcp.tool
async def delete_record_attachment(community: str, record_id: str, attachment_id: str) -> Dict:
    """Delete a record attachment"""
    return await get_client().make_request("DELETE", f"/records/{record_id}/attachments/{attachment_id}", community)

# RECORD WORKFLOW STEPS

@mcp.tool
async def get_record_workflow_steps(community: str, record_id: str) -> Dict:
    """Get workflow steps for a record"""
    return await get_client().make_request("GET", f"/records/{record_id}/workflowSteps", community)

@mcp.tool
async def get_record_workflow_step(community: str, record_id: str, step_id: str) -> Dict:
    """Get a specific workflow step"""
    return await get_client().make_request("GET", f"/records/{record_id}/workflowSteps/{step_id}", community)

@mcp.tool
async def update_record_workflow_step(community: str, record_id: str, step_id: str, step_data: Dict) -> Dict:
    """Update a workflow step"""
    return await get_client().make_request("PUT", f"/records/{record_id}/workflowSteps/{step_id}", community, json_data=step_data)

# RECORD WORKFLOW STEP COMMENTS

@mcp.tool
async def get_record_step_comments(community: str, record_id: str, step_id: str) -> Dict:
    """Get comments for a workflow step"""
    return await get_client().make_request("GET", f"/records/{record_id}/workflowSteps/{step_id}/comments", community)

@mcp.tool
async def create_record_step_comment(community: str, record_id: str, step_id: str, comment_data: Dict) -> Dict:
    """Create a comment on a workflow step"""
    return await get_client().make_request("POST", f"/records/{record_id}/workflowSteps/{step_id}/comments", community, json_data=comment_data)

@mcp.tool
async def delete_record_step_comment(community: str, record_id: str, step_id: str, comment_id: str) -> Dict:
    """Delete a workflow step comment"""
    return await get_client().make_request("DELETE", f"/records/{record_id}/workflowSteps/{step_id}/comments/{comment_id}", community)

# RECORD FORMS

@mcp.tool
async def get_record_form_details(community: str, record_id: str) -> Dict:
    """Get form details for a record"""
    return await get_client().make_request("GET", f"/records/{record_id}/details", community)

@mcp.tool
async def get_record_form_field(community: str, record_id: str, form_field_id: str) -> Dict:
    """Get a specific form field"""
    return await get_client().make_request("GET", f"/records/{record_id}/details/{form_field_id}", community)

@mcp.tool
async def update_record_form_field(community: str, record_id: str, form_field_id: str, field_data: Dict) -> Dict:
    """Update a form field"""
    return await get_client().make_request("PUT", f"/records/{record_id}/details/{form_field_id}", community, json_data=field_data)

# RECORD LOCATIONS

@mcp.tool
async def get_record_primary_location(community: str, record_id: str) -> Dict:
    """Get the primary location for a record"""
    return await get_client().make_request("GET", f"/records/{record_id}/primaryLocation", community)

@mcp.tool
async def update_record_primary_location(community: str, record_id: str, location_data: Dict) -> Dict:
    """Update the primary location for a record"""
    return await get_client().make_request("PUT", f"/records/{record_id}/primaryLocation", community, json_data=location_data)

@mcp.tool
async def get_record_additional_locations(community: str, record_id: str) -> Dict:
    """Get additional locations for a record"""
    return await get_client().make_request("GET", f"/records/{record_id}/additionalLocations", community)

@mcp.tool
async def add_record_additional_location(community: str, record_id: str, location_data: Dict) -> Dict:
    """Add an additional location to a record"""
    return await get_client().make_request("POST", f"/records/{record_id}/additionalLocations", community, json_data=location_data)

@mcp.tool
async def remove_record_additional_location(community: str, record_id: str, location_id: str) -> Dict:
    """Remove an additional location from a record"""
    return await get_client().make_request("DELETE", f"/records/{record_id}/additionalLocations/{location_id}", community)

# RECORD APPLICANT AND GUESTS

@mcp.tool
async def get_record_applicant(community: str, record_id: str) -> Dict:
    """Get the applicant for a record"""
    return await get_client().make_request("GET", f"/records/{record_id}/applicant", community)

@mcp.tool
async def get_record_guests(community: str, record_id: str) -> Dict:
    """Get guests for a record"""
    return await get_client().make_request("GET", f"/records/{record_id}/guests", community)

@mcp.tool
async def add_record_guest(community: str, record_id: str, guest_data: Dict) -> Dict:
    """Add a guest to a record"""
    return await get_client().make_request("POST", f"/records/{record_id}/guests", community, json_data=guest_data)

@mcp.tool
async def remove_record_guest(community: str, record_id: str, user_id: str) -> Dict:
    """Remove a guest from a record"""
    return await get_client().make_request("DELETE", f"/records/{record_id}/guests/{user_id}", community)

# RECORD CHANGE REQUESTS

@mcp.tool
async def get_record_change_requests(community: str, record_id: str) -> Dict:
    """Get change requests for a record"""
    return await get_client().make_request("GET", f"/records/{record_id}/changeRequests", community)

@mcp.tool
async def create_record_change_request(community: str, record_id: str, change_request_data: Dict) -> Dict:
    """Create a change request for a record"""
    return await get_client().make_request("POST", f"/records/{record_id}/changeRequests", community, json_data=change_request_data)

@mcp.tool
async def get_record_change_request(community: str, record_id: str, change_request_id: str) -> Dict:
    """Get a specific change request"""
    return await get_client().make_request("GET", f"/records/{record_id}/changeRequests/{change_request_id}", community)

# LOCATIONS

@mcp.tool
async def get_locations(community: str) -> Dict:
    """Get a list of locations
    
    Note: The OpenGov API does not support pagination parameters for this endpoint.
    All locations are returned in a single response.
    """
    return await get_client().make_request("GET", "/locations", community)

@mcp.tool
async def get_location(community: str, location_id: str) -> Dict:
    """Get a specific location by ID"""
    return await get_client().make_request("GET", f"/locations/{location_id}", community)

@mcp.tool
async def create_location(community: str, location_data: Dict) -> Dict:
    """Create a new location"""
    return await get_client().make_request("POST", "/locations", community, json_data=location_data)

@mcp.tool
async def update_location(community: str, location_id: str, location_data: Dict) -> Dict:
    """Update a location"""
    return await get_client().make_request("PUT", f"/locations/{location_id}", community, json_data=location_data)

@mcp.tool
async def get_location_flags(community: str, location_id: str) -> Dict:
    """Get flags for a location"""
    return await get_client().make_request("GET", f"/locations/{location_id}/flags", community)

# USERS

@mcp.tool
async def get_users(community: str) -> Dict:
    """Get a list of users
    
    Note: The OpenGov API does not support pagination or search parameters for this endpoint.
    All users are returned in a single response.
    """
    return await get_client().make_request("GET", "/users", community)

@mcp.tool
async def get_user(community: str, user_id: str) -> Dict:
    """Get a specific user by ID"""
    return await get_client().make_request("GET", f"/users/{user_id}", community)

@mcp.tool
async def create_user(community: str, user_data: Dict) -> Dict:
    """Create a new user"""
    return await get_client().make_request("POST", "/users", community, json_data=user_data)

@mcp.tool
async def update_user(community: str, user_id: str, user_data: Dict) -> Dict:
    """Update a user"""
    return await get_client().make_request("PUT", f"/users/{user_id}", community, json_data=user_data)

@mcp.tool
async def get_user_flags(community: str, user_id: str) -> Dict:
    """Get flags for a user"""
    return await get_client().make_request("GET", f"/users/{user_id}/flags", community)

# DEPARTMENTS

@mcp.tool
async def get_departments(community: str) -> Dict:
    """Get a list of departments"""
    return await get_client().make_request("GET", "/departments", community)

@mcp.tool
async def get_department(community: str, department_id: str) -> Dict:
    """Get a specific department by ID"""
    return await get_client().make_request("GET", f"/departments/{department_id}", community)

# RECORD TYPES

@mcp.tool
async def get_record_types(community: str) -> Dict:
    """Get a list of record types"""
    return await get_client().make_request("GET", "/recordTypes", community)

@mcp.tool
async def get_record_type(community: str, record_type_id: str) -> Dict:
    """Get a specific record type by ID"""
    return await get_client().make_request("GET", f"/recordTypes/{record_type_id}", community)

@mcp.tool
async def get_record_type_form(community: str, record_type_id: str) -> Dict:
    """Get form configuration for a record type"""
    return await get_client().make_request("GET", f"/recordTypes/{record_type_id}/form", community)

@mcp.tool
async def get_record_type_workflow(community: str, record_type_id: str) -> Dict:
    """Get workflow configuration for a record type"""
    return await get_client().make_request("GET", f"/recordTypes/{record_type_id}/workflow", community)

@mcp.tool
async def get_record_type_attachments(community: str, record_type_id: str) -> Dict:
    """Get attachment configurations for a record type"""
    return await get_client().make_request("GET", f"/recordTypes/{record_type_id}/attachments", community)

@mcp.tool
async def get_record_type_fees(community: str, record_type_id: str) -> Dict:
    """Get fee configurations for a record type"""
    return await get_client().make_request("GET", f"/recordTypes/{record_type_id}/fees", community)

@mcp.tool
async def get_record_type_document_templates(community: str, record_type_id: str) -> Dict:
    """Get document template configurations for a record type"""
    return await get_client().make_request("GET", f"/recordTypes/{record_type_id}/documentTemplates", community)

# PROJECTS

@mcp.tool
async def get_projects(community: str) -> Dict:
    """Get a list of projects
    
    Note: The OpenGov API does not support pagination parameters for this endpoint.
    All projects are returned in a single response.
    """
    return await get_client().make_request("GET", "/projects", community)

# INSPECTION STEPS

@mcp.tool
async def get_inspection_steps(community: str, limit: int = 100, offset: int = 0) -> Dict:
    """Get inspection steps"""
    params = {"limit": limit, "offset": offset}
    return await get_client().make_request("GET", "/inspectionSteps", community, params=params)

@mcp.tool
async def get_inspection_step(community: str, inspection_step_id: str) -> Dict:
    """Get a specific inspection step"""
    return await get_client().make_request("GET", f"/inspectionSteps/{inspection_step_id}", community)

@mcp.tool
async def update_inspection_step(community: str, inspection_step_id: str, step_data: Dict) -> Dict:
    """Update an inspection step"""
    return await get_client().make_request("PUT", f"/inspectionSteps/{inspection_step_id}", community, json_data=step_data)

@mcp.tool
async def get_inspection_step_types(community: str, inspection_step_id: str) -> Dict:
    """Get inspection types for an inspection step"""
    return await get_client().make_request("GET", f"/inspectionSteps/{inspection_step_id}/inspectionTypes", community)

# INSPECTION EVENTS

@mcp.tool
async def get_inspection_events(community: str, limit: int = 100, offset: int = 0) -> Dict:
    """Get inspection events"""
    params = {"limit": limit, "offset": offset}
    return await get_client().make_request("GET", "/inspectionEvents", community, params=params)

@mcp.tool
async def get_inspection_event(community: str, inspection_event_id: str) -> Dict:
    """Get a specific inspection event"""
    return await get_client().make_request("GET", f"/inspectionEvents/{inspection_event_id}", community)

@mcp.tool
async def create_inspection_event(community: str, event_data: Dict) -> Dict:
    """Create an inspection event"""
    return await get_client().make_request("POST", "/inspectionEvents", community, json_data=event_data)

@mcp.tool
async def update_inspection_event(community: str, inspection_event_id: str, event_data: Dict) -> Dict:
    """Update an inspection event"""
    return await get_client().make_request("PUT", f"/inspectionEvents/{inspection_event_id}", community, json_data=event_data)

# INSPECTION RESULTS

@mcp.tool
async def get_inspection_results(community: str, limit: int = 100, offset: int = 0) -> Dict:
    """Get inspection results"""
    params = {"limit": limit, "offset": offset}
    return await get_client().make_request("GET", "/inspectionResults", community, params=params)

@mcp.tool
async def get_inspection_result(community: str, inspection_result_id: str) -> Dict:
    """Get a specific inspection result"""
    return await get_client().make_request("GET", f"/inspectionResults/{inspection_result_id}", community)

@mcp.tool
async def create_inspection_result(community: str, result_data: Dict) -> Dict:
    """Create an inspection result"""
    return await get_client().make_request("POST", "/inspectionResults", community, json_data=result_data)

@mcp.tool
async def update_inspection_result(community: str, inspection_result_id: str, result_data: Dict) -> Dict:
    """Update an inspection result"""
    return await get_client().make_request("PUT", f"/inspectionResults/{inspection_result_id}", community, json_data=result_data)

# CHECKLIST RESULTS

@mcp.tool
async def get_checklist_results(community: str, inspection_result_id: str) -> Dict:
    """Get checklist results for an inspection result"""
    return await get_client().make_request("GET", f"/inspectionResults/{inspection_result_id}/checklistResults", community)

@mcp.tool
async def get_checklist_result(community: str, inspection_result_id: str, checklist_result_id: str) -> Dict:
    """Get a specific checklist result"""
    return await get_client().make_request("GET", f"/inspectionResults/{inspection_result_id}/checklistResults/{checklist_result_id}", community)

@mcp.tool
async def create_checklist_result(community: str, inspection_result_id: str, checklist_data: Dict) -> Dict:
    """Create a checklist result"""
    return await get_client().make_request("POST", f"/inspectionResults/{inspection_result_id}/checklistResults", community, json_data=checklist_data)

@mcp.tool
async def update_checklist_result(community: str, inspection_result_id: str, checklist_result_id: str, checklist_data: Dict) -> Dict:
    """Update a checklist result"""
    return await get_client().make_request("PUT", f"/inspectionResults/{inspection_result_id}/checklistResults/{checklist_result_id}", community, json_data=checklist_data)

# INSPECTION TYPE TEMPLATES

@mcp.tool
async def get_inspection_type_templates(community: str) -> Dict:
    """Get inspection type templates"""
    return await get_client().make_request("GET", "/inspectionTypeTemplates", community)

@mcp.tool
async def get_inspection_type_template(community: str, template_id: str) -> Dict:
    """Get a specific inspection type template"""
    return await get_client().make_request("GET", f"/inspectionTypeTemplates/{template_id}", community)

@mcp.tool
async def get_checklist_templates(community: str, template_id: str) -> Dict:
    """Get checklist templates for an inspection type template"""
    return await get_client().make_request("GET", f"/inspectionTypeTemplates/{template_id}/checklistTemplates", community)

@mcp.tool
async def get_checklist_template(community: str, template_id: str, checklist_template_id: str) -> Dict:
    """Get a specific checklist template"""
    return await get_client().make_request("GET", f"/inspectionTypeTemplates/{template_id}/checklistTemplates/{checklist_template_id}", community)

# APPROVAL STEPS

@mcp.tool
async def get_approval_steps(community: str, limit: int = 100, offset: int = 0) -> Dict:
    """Get approval steps"""
    params = {"limit": limit, "offset": offset}
    return await get_client().make_request("GET", "/approvalSteps", community, params=params)

@mcp.tool
async def get_approval_step(community: str, approval_step_id: str) -> Dict:
    """Get a specific approval step"""
    return await get_client().make_request("GET", f"/approvalSteps/{approval_step_id}", community)

@mcp.tool
async def update_approval_step(community: str, approval_step_id: str, step_data: Dict) -> Dict:
    """Update an approval step"""
    return await get_client().make_request("PUT", f"/approvalSteps/{approval_step_id}", community, json_data=step_data)

# DOCUMENT STEPS

@mcp.tool
async def get_document_steps(community: str, limit: int = 100, offset: int = 0) -> Dict:
    """Get document generation steps"""
    params = {"limit": limit, "offset": offset}
    return await get_client().make_request("GET", "/documentSteps", community, params=params)

@mcp.tool
async def get_document_step(community: str, document_step_id: str) -> Dict:
    """Get a specific document generation step"""
    return await get_client().make_request("GET", f"/documentSteps/{document_step_id}", community)

@mcp.tool
async def update_document_step(community: str, document_step_id: str, step_data: Dict) -> Dict:
    """Update a document generation step"""
    return await get_client().make_request("PUT", f"/documentSteps/{document_step_id}", community, json_data=step_data)

# PAYMENT STEPS

@mcp.tool
async def get_payment_steps(community: str, limit: int = 100, offset: int = 0) -> Dict:
    """Get payment steps"""
    params = {"limit": limit, "offset": offset}
    return await get_client().make_request("GET", "/paymentSteps", community, params=params)

@mcp.tool
async def get_payment_step(community: str, payment_step_id: str) -> Dict:
    """Get a specific payment step"""
    return await get_client().make_request("GET", f"/paymentSteps/{payment_step_id}", community)

@mcp.tool
async def update_payment_step(community: str, payment_step_id: str, step_data: Dict) -> Dict:
    """Update a payment step"""
    return await get_client().make_request("PUT", f"/paymentSteps/{payment_step_id}", community, json_data=step_data)

@mcp.tool
async def get_payment_fees(community: str, payment_step_id: str) -> Dict:
    """Get fees for a payment step"""
    return await get_client().make_request("GET", f"/paymentSteps/{payment_step_id}/fees", community)

@mcp.tool
async def get_payment_fee(community: str, payment_fee_id: str) -> Dict:
    """Get a specific payment fee"""
    return await get_client().make_request("GET", f"/paymentSteps/fees/{payment_fee_id}", community)

# TRANSACTIONS

@mcp.tool
async def get_transactions(community: str, limit: int = 100, offset: int = 0) -> Dict:
    """Get payment transactions"""
    params = {"limit": limit, "offset": offset}
    return await get_client().make_request("GET", "/transactions", community, params=params)

@mcp.tool
async def get_transaction(community: str, transaction_id: str) -> Dict:
    """Get a specific transaction"""
    return await get_client().make_request("GET", f"/transactions/{transaction_id}", community)

# LEDGER ENTRIES

@mcp.tool
async def get_ledger_entries(community: str, limit: int = 100, offset: int = 0) -> Dict:
    """Get ledger entries"""
    params = {"limit": limit, "offset": offset}
    return await get_client().make_request("GET", "/ledgerEntries", community, params=params)

@mcp.tool
async def get_ledger_entry(community: str, ledger_id: str) -> Dict:
    """Get a specific ledger entry"""
    return await get_client().make_request("GET", f"/ledgerEntries/{ledger_id}", community)

# FILES

@mcp.tool
async def get_files(community: str, limit: int = 100, offset: int = 0) -> Dict:
    """Get files"""
    params = {"limit": limit, "offset": offset}
    return await get_client().make_request("GET", "/files", community, params=params)

@mcp.tool
async def get_file(community: str, file_id: str) -> Dict:
    """Get a specific file"""
    return await get_client().make_request("GET", f"/files/{file_id}", community)

@mcp.tool
async def create_file(community: str, file_data: Dict) -> Dict:
    """Create a file entry for upload"""
    return await get_client().make_request("POST", "/files", community, json_data=file_data)

@mcp.tool
async def update_file(community: str, file_id: str, file_data: Dict) -> Dict:
    """Update file metadata"""
    return await get_client().make_request("PUT", f"/files/{file_id}", community, json_data=file_data)

@mcp.tool
async def delete_file(community: str, file_id: str) -> Dict:
    """Delete a file"""
    return await get_client().make_request("DELETE", f"/files/{file_id}", community)

# ORGANIZATION

@mcp.tool
async def get_organization(community: str) -> Dict:
    """Get organization information"""
    return await get_client().make_request("GET", "/organization", community)

if __name__ == "__main__":
    # Run the server
    import sys
    
    # Default to stdio transport for LangGraph compatibility
    transport = "stdio"
    
    # Check for command line argument to use HTTP transport
    if len(sys.argv) > 1 and sys.argv[1] == "--http":
        transport = "streamable-http"
        print("Starting OpenGov PLC MCP Server on HTTP transport...")
    else:
        print("Starting OpenGov PLC MCP Server on stdio transport...")
    
    mcp.run(transport=transport) 