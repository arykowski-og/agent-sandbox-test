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
from urllib.parse import quote
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
                    
                    # Handle specific error cases with more helpful messages
                    if response.status == 403:
                        return {
                            "error": "Access forbidden",
                            "status": 403,
                            "message": f"Access denied to {endpoint}. This may be due to insufficient permissions or the resource may not exist.",
                            "url": url,
                            "details": error_text
                        }
                    elif response.status == 404:
                        return {
                            "error": "Resource not found",
                            "status": 404,
                            "message": f"The requested resource at {endpoint} was not found.",
                            "url": url,
                            "details": error_text
                        }
                    elif response.status == 401:
                        return {
                            "error": "Authentication failed",
                            "status": 401,
                            "message": "Authentication failed. Please check your API credentials.",
                            "url": url,
                            "details": error_text
                        }
                    else:
                        return {
                            "error": "API request failed",
                            "status": response.status,
                            "message": f"API request to {endpoint} failed with status {response.status}",
                            "url": url,
                            "details": error_text
                        }
                
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

def encode_path_param(param: str) -> str:
    """URL encode a path parameter"""
    return quote(str(param), safe='')

# RECORD TOOLS

@mcp.tool
async def get_records(
    community: str,
    filter_number: str = None,
    filter_hist_id: str = None,
    filter_hist_number: str = None,
    filter_type_id: str = None,
    filter_project_id: str = None,
    filter_status: str = None,
    filter_created_at_from: str = None,
    filter_created_at_to: str = None,
    filter_updated_at_from: str = None,
    filter_updated_at_to: str = None,
    filter_submitted_at_from: str = None,
    filter_submitted_at_to: str = None,
    filter_expires_at_from: str = None,
    filter_expires_at_to: str = None,
    filter_is_enabled: bool = None,
    filter_renewal_submitted: bool = None,
    filter_submitted_online: bool = None,
    filter_renewal_number: str = None,
    filter_renewal_of_record_id: str = None,
    page_number: int = 1,
    page_size: int = 20,
    include_enhanced_details: bool = True
) -> Dict:
    """Get a list of records from the community with optional filtering, pagination, and enhanced details
    
    Args:
        community: The community identifier
        filter_number: Filter by record number
        filter_hist_id: Filter by historical ID
        filter_hist_number: Filter by historical permit number
        filter_type_id: Filter by record type ID
        filter_project_id: Filter by project ID
        filter_status: Filter by status (STOPPED, DRAFT, ACTIVE, COMPLETE)
        filter_created_at_from: Filter by creation date (from)
        filter_created_at_to: Filter by creation date (to)
        filter_updated_at_from: Filter by last updated date (from)
        filter_updated_at_to: Filter by last updated date (to)
        filter_submitted_at_from: Filter by submission date (from)
        filter_submitted_at_to: Filter by submission date (to)
        filter_expires_at_from: Filter by expiration date (from)
        filter_expires_at_to: Filter by expiration date (to)
        filter_is_enabled: Filter by enabled status
        filter_renewal_submitted: Filter by renewal submission status
        filter_submitted_online: Filter by online submission status
        filter_renewal_number: Filter by renewal number
        filter_renewal_of_record_id: Filter by renewal of record ID
        page_number: Which page to return (1-based, default: 1)
        page_size: Number of records per page (1-100, default: 20)
        include_enhanced_details: Whether to fetch location and application details (default: True)
    
    This enhanced version can optionally fetch additional details for each record:
    - Primary location address
    - Application name from form details
    
    Set include_enhanced_details=False for faster responses when you only need basic record data.
    """
    try:
        # Build query parameters
        params = {}
        
        # Add filters
        if filter_number:
            params["filter[number]"] = filter_number
        if filter_hist_id:
            params["filter[histID]"] = filter_hist_id
        if filter_hist_number:
            params["filter[histNumber]"] = filter_hist_number
        if filter_type_id:
            params["filter[typeID]"] = filter_type_id
        if filter_project_id:
            params["filter[projectID]"] = filter_project_id
        if filter_status:
            params["filter[status]"] = filter_status
        if filter_is_enabled is not None:
            params["filter[isEnabled]"] = str(filter_is_enabled).lower()
        if filter_renewal_submitted is not None:
            params["filter[renewalSubmitted]"] = str(filter_renewal_submitted).lower()
        if filter_submitted_online is not None:
            params["filter[submittedOnline]"] = str(filter_submitted_online).lower()
        if filter_renewal_number:
            params["filter[renewalNumber]"] = filter_renewal_number
        if filter_renewal_of_record_id:
            params["filter[renewalOfRecordID]"] = filter_renewal_of_record_id
        
        # Add date range filters
        if filter_created_at_from:
            params["filter[createdAt][from]"] = filter_created_at_from
        if filter_created_at_to:
            params["filter[createdAt][to]"] = filter_created_at_to
        if filter_updated_at_from:
            params["filter[updatedAt][from]"] = filter_updated_at_from
        if filter_updated_at_to:
            params["filter[updatedAt][to]"] = filter_updated_at_to
        if filter_submitted_at_from:
            params["filter[submittedAt][from]"] = filter_submitted_at_from
        if filter_submitted_at_to:
            params["filter[submittedAt][to]"] = filter_submitted_at_to
        if filter_expires_at_from:
            params["filter[expiresAt][from]"] = filter_expires_at_from
        if filter_expires_at_to:
            params["filter[expiresAt][to]"] = filter_expires_at_to
        
        # Add pagination
        if page_number and page_number >= 1:
            params["page[number]"] = page_number
        if page_size and 1 <= page_size <= 100:
            params["page[size]"] = page_size
        
        # Get the basic records list
        records_result = await get_client().make_request("GET", "/records", community, params=params)
        
        if "data" not in records_result or not isinstance(records_result["data"], list):
            return records_result
        
        # If enhanced details are not requested, return the basic result
        if not include_enhanced_details:
            return records_result
        
        # Enhance each record with location and application details
        enhanced_records = []
        client = get_client()
        
        for record in records_result["data"]:
            enhanced_record = record.copy()
            record_id = record.get("id")
            
            if record_id:
                # Fetch primary location address
                try:
                    location_result = await client.make_request("GET", f"/records/{encode_path_param(record_id)}/primaryLocation", community)
                    if "data" in location_result:
                        location_data = location_result["data"]
                        # Extract address information
                        address_parts = []
                        if location_data.get("streetNumber"):
                            address_parts.append(str(location_data["streetNumber"]))
                        if location_data.get("streetName"):
                            address_parts.append(location_data["streetName"])
                        if location_data.get("city"):
                            address_parts.append(location_data["city"])
                        if location_data.get("state"):
                            address_parts.append(location_data["state"])
                        if location_data.get("zipCode"):
                            address_parts.append(location_data["zipCode"])
                        
                        enhanced_record["locationAddress"] = ", ".join(address_parts) if address_parts else None
                        enhanced_record["locationDetails"] = location_data
                    else:
                        enhanced_record["locationAddress"] = None
                        enhanced_record["locationDetails"] = None
                except Exception as e:
                    enhanced_record["locationAddress"] = None
                    enhanced_record["locationDetails"] = None
                    enhanced_record["locationError"] = str(e)
                
                # Fetch application name from form details
                try:
                    form_result = await client.make_request("GET", f"/records/{encode_path_param(record_id)}/details", community)
                    if "data" in form_result and isinstance(form_result["data"], list):
                        # Look for common application name fields
                        application_name = None
                        for field in form_result["data"]:
                            field_name = field.get("name", "").lower()
                            if any(keyword in field_name for keyword in ["application", "project", "name", "title"]):
                                application_name = field.get("value")
                                if application_name:
                                    break
                        
                        enhanced_record["applicationName"] = application_name
                        enhanced_record["formDetails"] = form_result["data"]
                    else:
                        enhanced_record["applicationName"] = None
                        enhanced_record["formDetails"] = None
                except Exception as e:
                    enhanced_record["applicationName"] = None
                    enhanced_record["formDetails"] = None
                    enhanced_record["formError"] = str(e)
            else:
                enhanced_record["locationAddress"] = None
                enhanced_record["locationDetails"] = None
                enhanced_record["applicationName"] = None
                enhanced_record["formDetails"] = None
            
            enhanced_records.append(enhanced_record)
        
        # Return the enhanced result
        enhanced_result = records_result.copy()
        enhanced_result["data"] = enhanced_records
        return enhanced_result
        
    except Exception as e:
        return {
            "error": "Failed to fetch enhanced records",
            "message": str(e),
            "fallback": "Try using the basic get_records function if this enhanced version fails"
        }

@mcp.tool
async def list_available_record_ids(community: str) -> Dict:
    """Get a list of available record IDs in the community
    
    This is a helper function to see what record IDs are actually available,
    which can be useful when the get_record function fails due to invalid IDs.
    """
    try:
        records_result = await get_client().make_request("GET", "/records", community)
        
        if "data" in records_result and isinstance(records_result["data"], list):
            record_info = []
            for record in records_result["data"]:
                info = {
                    "id": record.get("id"),
                    "recordNumber": record.get("recordNumber"),
                    "recordType": record.get("recordType", {}).get("name"),
                    "status": record.get("status"),
                    "createdAt": record.get("createdAt")
                }
                record_info.append(info)
            
            return {
                "success": True,
                "total_records": len(record_info),
                "records": record_info
            }
        else:
            return {
                "success": False,
                "message": "No records found or unexpected response format",
                "raw_response": records_result
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to retrieve records list"
        }

@mcp.tool
async def get_record(community: str, record_id: str) -> Dict:
    """Get a specific record by ID
    
    Note: Due to an issue with the OpenGov API where it sometimes fails to substitute
    path parameters correctly, this function will first try the direct API endpoint,
    and if that fails, it will search through all records to find a match.
    
    If you're getting errors, try using list_available_record_ids() first to see
    what record IDs are actually available.
    """
    
    # First try the direct API endpoint approach
    try:
        result = await get_client().make_request("GET", f"/records/{encode_path_param(record_id)}", community)
        if "error" not in result:
            return result
    except Exception:
        pass  # Fall through to alternative approach
    
    # If the direct approach fails, try searching through all records
    try:
        all_records = await get_client().make_request("GET", "/records", community)
        
        if "data" in all_records and isinstance(all_records["data"], list):
            # Look for a record with matching ID in various possible fields
            for record in all_records["data"]:
                # Check different possible ID fields
                possible_ids = [
                    record.get("id"),
                    record.get("recordId"), 
                    record.get("recordNumber"),
                    str(record.get("id")) if record.get("id") else None,
                ]
                
                if record_id in possible_ids or str(record_id) in [str(pid) for pid in possible_ids if pid is not None]:
                    return {"data": record}
            
        # If no match found, return helpful error
        return {
            "error": "Record not found",
            "status": 404,
            "message": f"Could not find record with ID '{record_id}'. Use list_available_record_ids() to see available records.",
            "suggestion": f"Try calling list_available_record_ids('{community}') to see what record IDs are available."
        }
        
    except Exception as e:
        return {
            "error": "API request failed",
            "status": 500,
            "message": f"Failed to retrieve record '{record_id}'. This may be due to an OpenGov API issue.",
            "details": str(e),
            "suggestion": f"Try calling list_available_record_ids('{community}') to see available records."
        }

@mcp.tool
async def create_record(community: str, record_data: Dict) -> Dict:
    """Create a new record"""
    return await get_client().make_request("POST", "/records", community, json_data=record_data)

@mcp.tool
async def update_record(community: str, record_id: str, record_data: Dict) -> Dict:
    """Update an existing record"""
    return await get_client().make_request("PUT", f"/records/{encode_path_param(record_id)}", community, json_data=record_data)

@mcp.tool
async def delete_record(community: str, record_id: str) -> Dict:
    """Delete a record"""
    return await get_client().make_request("DELETE", f"/records/{encode_path_param(record_id)}", community)

# RECORD ATTACHMENTS

@mcp.tool
async def get_record_attachments(community: str, record_id: str) -> Dict:
    """Get attachments for a record"""
    return await get_client().make_request("GET", f"/records/{encode_path_param(record_id)}/attachments", community)

@mcp.tool
async def get_record_attachment(community: str, record_id: str, attachment_id: str) -> Dict:
    """Get a specific record attachment"""
    return await get_client().make_request("GET", f"/records/{encode_path_param(record_id)}/attachments/{encode_path_param(attachment_id)}", community)

@mcp.tool
async def create_record_attachment(community: str, record_id: str, attachment_data: Dict) -> Dict:
    """Create a new record attachment"""
    return await get_client().make_request("POST", f"/records/{encode_path_param(record_id)}/attachments", community, json_data=attachment_data)

@mcp.tool
async def update_record_attachment(community: str, record_id: str, attachment_id: str, attachment_data: Dict) -> Dict:
    """Update a record attachment"""
    return await get_client().make_request("PUT", f"/records/{encode_path_param(record_id)}/attachments/{encode_path_param(attachment_id)}", community, json_data=attachment_data)

@mcp.tool
async def delete_record_attachment(community: str, record_id: str, attachment_id: str) -> Dict:
    """Delete a record attachment"""
    return await get_client().make_request("DELETE", f"/records/{encode_path_param(record_id)}/attachments/{encode_path_param(attachment_id)}", community)

# RECORD WORKFLOW STEPS

@mcp.tool
async def get_record_workflow_steps(community: str, record_id: str) -> Dict:
    """Get workflow steps for a record"""
    return await get_client().make_request("GET", f"/records/{encode_path_param(record_id)}/workflowSteps", community)

@mcp.tool
async def get_record_workflow_step(community: str, record_id: str, step_id: str) -> Dict:
    """Get a specific workflow step"""
    return await get_client().make_request("GET", f"/records/{encode_path_param(record_id)}/workflowSteps/{encode_path_param(step_id)}", community)

@mcp.tool
async def update_record_workflow_step(community: str, record_id: str, step_id: str, step_data: Dict) -> Dict:
    """Update a workflow step"""
    return await get_client().make_request("PUT", f"/records/{encode_path_param(record_id)}/workflowSteps/{encode_path_param(step_id)}", community, json_data=step_data)

# RECORD WORKFLOW STEP COMMENTS

@mcp.tool
async def get_record_step_comments(community: str, record_id: str, step_id: str) -> Dict:
    """Get comments for a workflow step"""
    return await get_client().make_request("GET", f"/records/{encode_path_param(record_id)}/workflowSteps/{encode_path_param(step_id)}/comments", community)

@mcp.tool
async def create_record_step_comment(community: str, record_id: str, step_id: str, comment_data: Dict) -> Dict:
    """Create a comment on a workflow step"""
    return await get_client().make_request("POST", f"/records/{encode_path_param(record_id)}/workflowSteps/{encode_path_param(step_id)}/comments", community, json_data=comment_data)

@mcp.tool
async def delete_record_step_comment(community: str, record_id: str, step_id: str, comment_id: str) -> Dict:
    """Delete a workflow step comment"""
    return await get_client().make_request("DELETE", f"/records/{encode_path_param(record_id)}/workflowSteps/{encode_path_param(step_id)}/comments/{encode_path_param(comment_id)}", community)

# RECORD FORMS

@mcp.tool
async def get_record_form_details(community: str, record_id: str) -> Dict:
    """Get form details for a record"""
    return await get_client().make_request("GET", f"/records/{encode_path_param(record_id)}/details", community)

@mcp.tool
async def get_record_form_field(community: str, record_id: str, form_field_id: str) -> Dict:
    """Get a specific form field"""
    return await get_client().make_request("GET", f"/records/{encode_path_param(record_id)}/details/{encode_path_param(form_field_id)}", community)

@mcp.tool
async def update_record_form_field(community: str, record_id: str, form_field_id: str, field_data: Dict) -> Dict:
    """Update a form field"""
    return await get_client().make_request("PUT", f"/records/{encode_path_param(record_id)}/details/{encode_path_param(form_field_id)}", community, json_data=field_data)

# RECORD LOCATIONS

@mcp.tool
async def get_record_primary_location(community: str, record_id: str) -> Dict:
    """Get the primary location for a record"""
    return await get_client().make_request("GET", f"/records/{encode_path_param(record_id)}/primaryLocation", community)

@mcp.tool
async def update_record_primary_location(community: str, record_id: str, location_data: Dict) -> Dict:
    """Update the primary location for a record"""
    return await get_client().make_request("PUT", f"/records/{encode_path_param(record_id)}/primaryLocation", community, json_data=location_data)

@mcp.tool
async def get_record_additional_locations(community: str, record_id: str) -> Dict:
    """Get additional locations for a record"""
    return await get_client().make_request("GET", f"/records/{encode_path_param(record_id)}/additionalLocations", community)

@mcp.tool
async def add_record_additional_location(community: str, record_id: str, location_data: Dict) -> Dict:
    """Add an additional location to a record"""
    return await get_client().make_request("POST", f"/records/{encode_path_param(record_id)}/additionalLocations", community, json_data=location_data)

@mcp.tool
async def remove_record_additional_location(community: str, record_id: str, location_id: str) -> Dict:
    """Remove an additional location from a record"""
    return await get_client().make_request("DELETE", f"/records/{encode_path_param(record_id)}/additionalLocations/{encode_path_param(location_id)}", community)

# RECORD APPLICANT AND GUESTS

@mcp.tool
async def get_record_applicant(community: str, record_id: str) -> Dict:
    """Get the applicant for a record"""
    return await get_client().make_request("GET", f"/records/{encode_path_param(record_id)}/applicant", community)

@mcp.tool
async def get_record_guests(community: str, record_id: str) -> Dict:
    """Get guests for a record"""
    return await get_client().make_request("GET", f"/records/{encode_path_param(record_id)}/guests", community)

@mcp.tool
async def add_record_guest(community: str, record_id: str, guest_data: Dict) -> Dict:
    """Add a guest to a record"""
    return await get_client().make_request("POST", f"/records/{encode_path_param(record_id)}/guests", community, json_data=guest_data)

@mcp.tool
async def remove_record_guest(community: str, record_id: str, user_id: str) -> Dict:
    """Remove a guest from a record"""
    return await get_client().make_request("DELETE", f"/records/{encode_path_param(record_id)}/guests/{encode_path_param(user_id)}", community)

# RECORD CHANGE REQUESTS

@mcp.tool
async def get_record_change_requests(community: str, record_id: str) -> Dict:
    """Get change requests for a record"""
    return await get_client().make_request("GET", f"/records/{encode_path_param(record_id)}/changeRequests", community)

@mcp.tool
async def create_record_change_request(community: str, record_id: str, change_request_data: Dict) -> Dict:
    """Create a change request for a record"""
    return await get_client().make_request("POST", f"/records/{encode_path_param(record_id)}/changeRequests", community, json_data=change_request_data)

@mcp.tool
async def get_record_change_request(community: str, record_id: str, change_request_id: str) -> Dict:
    """Get a specific change request"""
    return await get_client().make_request("GET", f"/records/{encode_path_param(record_id)}/changeRequests/{encode_path_param(change_request_id)}", community)

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
    return await get_client().make_request("GET", f"/locations/{encode_path_param(location_id)}", community)

@mcp.tool
async def create_location(community: str, location_data: Dict) -> Dict:
    """Create a new location"""
    return await get_client().make_request("POST", "/locations", community, json_data=location_data)

@mcp.tool
async def update_location(community: str, location_id: str, location_data: Dict) -> Dict:
    """Update a location"""
    return await get_client().make_request("PUT", f"/locations/{encode_path_param(location_id)}", community, json_data=location_data)

@mcp.tool
async def get_location_flags(community: str, location_id: str) -> Dict:
    """Get flags for a location"""
    return await get_client().make_request("GET", f"/locations/{encode_path_param(location_id)}/flags", community)

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
    return await get_client().make_request("GET", f"/users/{encode_path_param(user_id)}", community)

@mcp.tool
async def create_user(community: str, user_data: Dict) -> Dict:
    """Create a new user"""
    return await get_client().make_request("POST", "/users", community, json_data=user_data)

@mcp.tool
async def update_user(community: str, user_id: str, user_data: Dict) -> Dict:
    """Update a user"""
    return await get_client().make_request("PUT", f"/users/{encode_path_param(user_id)}", community, json_data=user_data)

@mcp.tool
async def get_user_flags(community: str, user_id: str) -> Dict:
    """Get flags for a user"""
    return await get_client().make_request("GET", f"/users/{encode_path_param(user_id)}/flags", community)

# DEPARTMENTS

@mcp.tool
async def get_departments(community: str) -> Dict:
    """Get a list of departments"""
    return await get_client().make_request("GET", "/departments", community)

@mcp.tool
async def get_department(community: str, department_id: str) -> Dict:
    """Get a specific department by ID"""
    return await get_client().make_request("GET", f"/departments/{encode_path_param(department_id)}", community)

# RECORD TYPES

@mcp.tool
async def get_record_types(community: str) -> Dict:
    """Get a list of record types"""
    return await get_client().make_request("GET", "/recordTypes", community)

@mcp.tool
async def get_record_type(community: str, record_type_id: str) -> Dict:
    """Get a specific record type by ID"""
    return await get_client().make_request("GET", f"/recordTypes/{encode_path_param(record_type_id)}", community)

@mcp.tool
async def get_record_type_form(community: str, record_type_id: str) -> Dict:
    """Get form configuration for a record type"""
    return await get_client().make_request("GET", f"/recordTypes/{encode_path_param(record_type_id)}/form", community)

@mcp.tool
async def get_record_type_workflow(community: str, record_type_id: str) -> Dict:
    """Get workflow configuration for a record type"""
    return await get_client().make_request("GET", f"/recordTypes/{encode_path_param(record_type_id)}/workflow", community)

@mcp.tool
async def get_record_type_attachments(community: str, record_type_id: str) -> Dict:
    """Get attachment configurations for a record type"""
    return await get_client().make_request("GET", f"/recordTypes/{encode_path_param(record_type_id)}/attachments", community)

@mcp.tool
async def get_record_type_fees(community: str, record_type_id: str) -> Dict:
    """Get fee configurations for a record type"""
    return await get_client().make_request("GET", f"/recordTypes/{encode_path_param(record_type_id)}/fees", community)

@mcp.tool
async def get_record_type_document_templates(community: str, record_type_id: str) -> Dict:
    """Get document template configurations for a record type"""
    return await get_client().make_request("GET", f"/recordTypes/{encode_path_param(record_type_id)}/documentTemplates", community)

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
    return await get_client().make_request("GET", f"/inspectionSteps/{encode_path_param(inspection_step_id)}", community)

@mcp.tool
async def update_inspection_step(community: str, inspection_step_id: str, step_data: Dict) -> Dict:
    """Update an inspection step"""
    return await get_client().make_request("PUT", f"/inspectionSteps/{encode_path_param(inspection_step_id)}", community, json_data=step_data)

@mcp.tool
async def get_inspection_step_types(community: str, inspection_step_id: str) -> Dict:
    """Get inspection types for an inspection step"""
    return await get_client().make_request("GET", f"/inspectionSteps/{encode_path_param(inspection_step_id)}/inspectionTypes", community)

# INSPECTION EVENTS

@mcp.tool
async def get_inspection_events(community: str, limit: int = 100, offset: int = 0) -> Dict:
    """Get inspection events"""
    params = {"limit": limit, "offset": offset}
    return await get_client().make_request("GET", "/inspectionEvents", community, params=params)

@mcp.tool
async def get_inspection_event(community: str, inspection_event_id: str) -> Dict:
    """Get a specific inspection event"""
    return await get_client().make_request("GET", f"/inspectionEvents/{encode_path_param(inspection_event_id)}", community)

@mcp.tool
async def create_inspection_event(community: str, event_data: Dict) -> Dict:
    """Create an inspection event"""
    return await get_client().make_request("POST", "/inspectionEvents", community, json_data=event_data)

@mcp.tool
async def update_inspection_event(community: str, inspection_event_id: str, event_data: Dict) -> Dict:
    """Update an inspection event"""
    return await get_client().make_request("PUT", f"/inspectionEvents/{encode_path_param(inspection_event_id)}", community, json_data=event_data)

# INSPECTION RESULTS

@mcp.tool
async def get_inspection_results(community: str, limit: int = 100, offset: int = 0) -> Dict:
    """Get inspection results"""
    params = {"limit": limit, "offset": offset}
    return await get_client().make_request("GET", "/inspectionResults", community, params=params)

@mcp.tool
async def get_inspection_result(community: str, inspection_result_id: str) -> Dict:
    """Get a specific inspection result"""
    return await get_client().make_request("GET", f"/inspectionResults/{encode_path_param(inspection_result_id)}", community)

@mcp.tool
async def create_inspection_result(community: str, result_data: Dict) -> Dict:
    """Create an inspection result"""
    return await get_client().make_request("POST", "/inspectionResults", community, json_data=result_data)

@mcp.tool
async def update_inspection_result(community: str, inspection_result_id: str, result_data: Dict) -> Dict:
    """Update an inspection result"""
    return await get_client().make_request("PUT", f"/inspectionResults/{encode_path_param(inspection_result_id)}", community, json_data=result_data)

# CHECKLIST RESULTS

@mcp.tool
async def get_checklist_results(community: str, inspection_result_id: str) -> Dict:
    """Get checklist results for an inspection result"""
    return await get_client().make_request("GET", f"/inspectionResults/{encode_path_param(inspection_result_id)}/checklistResults", community)

@mcp.tool
async def get_checklist_result(community: str, inspection_result_id: str, checklist_result_id: str) -> Dict:
    """Get a specific checklist result"""
    return await get_client().make_request("GET", f"/inspectionResults/{encode_path_param(inspection_result_id)}/checklistResults/{encode_path_param(checklist_result_id)}", community)

@mcp.tool
async def create_checklist_result(community: str, inspection_result_id: str, checklist_data: Dict) -> Dict:
    """Create a checklist result"""
    return await get_client().make_request("POST", f"/inspectionResults/{encode_path_param(inspection_result_id)}/checklistResults", community, json_data=checklist_data)

@mcp.tool
async def update_checklist_result(community: str, inspection_result_id: str, checklist_result_id: str, checklist_data: Dict) -> Dict:
    """Update a checklist result"""
    return await get_client().make_request("PUT", f"/inspectionResults/{encode_path_param(inspection_result_id)}/checklistResults/{encode_path_param(checklist_result_id)}", community, json_data=checklist_data)

# INSPECTION TYPE TEMPLATES

@mcp.tool
async def get_inspection_type_templates(community: str) -> Dict:
    """Get inspection type templates"""
    return await get_client().make_request("GET", "/inspectionTypeTemplates", community)

@mcp.tool
async def get_inspection_type_template(community: str, template_id: str) -> Dict:
    """Get a specific inspection type template"""
    return await get_client().make_request("GET", f"/inspectionTypeTemplates/{encode_path_param(template_id)}", community)

@mcp.tool
async def get_checklist_templates(community: str, template_id: str) -> Dict:
    """Get checklist templates for an inspection type template"""
    return await get_client().make_request("GET", f"/inspectionTypeTemplates/{encode_path_param(template_id)}/checklistTemplates", community)

@mcp.tool
async def get_checklist_template(community: str, template_id: str, checklist_template_id: str) -> Dict:
    """Get a specific checklist template"""
    return await get_client().make_request("GET", f"/inspectionTypeTemplates/{encode_path_param(template_id)}/checklistTemplates/{encode_path_param(checklist_template_id)}", community)

# APPROVAL STEPS

@mcp.tool
async def get_approval_steps(community: str, limit: int = 100, offset: int = 0) -> Dict:
    """Get approval steps"""
    params = {"limit": limit, "offset": offset}
    return await get_client().make_request("GET", "/approvalSteps", community, params=params)

@mcp.tool
async def get_approval_step(community: str, approval_step_id: str) -> Dict:
    """Get a specific approval step"""
    return await get_client().make_request("GET", f"/approvalSteps/{encode_path_param(approval_step_id)}", community)

@mcp.tool
async def update_approval_step(community: str, approval_step_id: str, step_data: Dict) -> Dict:
    """Update an approval step"""
    return await get_client().make_request("PUT", f"/approvalSteps/{encode_path_param(approval_step_id)}", community, json_data=step_data)

# DOCUMENT STEPS

@mcp.tool
async def get_document_steps(community: str, limit: int = 100, offset: int = 0) -> Dict:
    """Get document generation steps"""
    params = {"limit": limit, "offset": offset}
    return await get_client().make_request("GET", "/documentSteps", community, params=params)

@mcp.tool
async def get_document_step(community: str, document_step_id: str) -> Dict:
    """Get a specific document generation step"""
    return await get_client().make_request("GET", f"/documentSteps/{encode_path_param(document_step_id)}", community)

@mcp.tool
async def update_document_step(community: str, document_step_id: str, step_data: Dict) -> Dict:
    """Update a document generation step"""
    return await get_client().make_request("PUT", f"/documentSteps/{encode_path_param(document_step_id)}", community, json_data=step_data)

# PAYMENT STEPS

@mcp.tool
async def get_payment_steps(community: str, limit: int = 100, offset: int = 0) -> Dict:
    """Get payment steps"""
    params = {"limit": limit, "offset": offset}
    return await get_client().make_request("GET", "/paymentSteps", community, params=params)

@mcp.tool
async def get_payment_step(community: str, payment_step_id: str) -> Dict:
    """Get a specific payment step"""
    return await get_client().make_request("GET", f"/paymentSteps/{encode_path_param(payment_step_id)}", community)

@mcp.tool
async def update_payment_step(community: str, payment_step_id: str, step_data: Dict) -> Dict:
    """Update a payment step"""
    return await get_client().make_request("PUT", f"/paymentSteps/{encode_path_param(payment_step_id)}", community, json_data=step_data)

@mcp.tool
async def get_payment_fees(community: str, payment_step_id: str) -> Dict:
    """Get fees for a payment step"""
    return await get_client().make_request("GET", f"/paymentSteps/{payment_step_id}/fees", community)

@mcp.tool
async def get_payment_fee(community: str, payment_fee_id: str) -> Dict:
    """Get a specific payment fee"""
    return await get_client().make_request("GET", f"/paymentSteps/fees/{encode_path_param(payment_fee_id)}", community)

# TRANSACTIONS

@mcp.tool
async def get_transactions(community: str, limit: int = 100, offset: int = 0) -> Dict:
    """Get payment transactions"""
    params = {"limit": limit, "offset": offset}
    return await get_client().make_request("GET", "/transactions", community, params=params)

@mcp.tool
async def get_transaction(community: str, transaction_id: str) -> Dict:
    """Get a specific transaction"""
    return await get_client().make_request("GET", f"/transactions/{encode_path_param(transaction_id)}", community)

# LEDGER ENTRIES

@mcp.tool
async def get_ledger_entries(community: str, limit: int = 100, offset: int = 0) -> Dict:
    """Get ledger entries"""
    params = {"limit": limit, "offset": offset}
    return await get_client().make_request("GET", "/ledgerEntries", community, params=params)

@mcp.tool
async def get_ledger_entry(community: str, ledger_id: str) -> Dict:
    """Get a specific ledger entry"""
    return await get_client().make_request("GET", f"/ledgerEntries/{encode_path_param(ledger_id)}", community)

# FILES

@mcp.tool
async def get_files(community: str, limit: int = 100, offset: int = 0) -> Dict:
    """Get files"""
    params = {"limit": limit, "offset": offset}
    return await get_client().make_request("GET", "/files", community, params=params)

@mcp.tool
async def get_file(community: str, file_id: str) -> Dict:
    """Get a specific file"""
    return await get_client().make_request("GET", f"/files/{encode_path_param(file_id)}", community)

@mcp.tool
async def create_file(community: str, file_data: Dict) -> Dict:
    """Create a file entry for upload"""
    return await get_client().make_request("POST", "/files", community, json_data=file_data)

@mcp.tool
async def update_file(community: str, file_id: str, file_data: Dict) -> Dict:
    """Update file metadata"""
    return await get_client().make_request("PUT", f"/files/{encode_path_param(file_id)}", community, json_data=file_data)

@mcp.tool
async def delete_file(community: str, file_id: str) -> Dict:
    """Delete a file"""
    return await get_client().make_request("DELETE", f"/files/{encode_path_param(file_id)}", community)

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