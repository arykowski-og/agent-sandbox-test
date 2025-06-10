"""Schema generator for dynamic UI components"""

import json
from typing import Dict, List, Any, Optional
from datetime import datetime

def format_date(date_string: Optional[str]) -> Optional[str]:
    """Format date string for display"""
    if not date_string:
        return None
    try:
        date = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
        return date.strftime('%m/%d/%Y')
    except:
        return date_string

def get_status_color(status: str) -> str:
    """Get color for status badge"""
    status_lower = status.lower() if status else ''
    if status_lower in ['active', 'approved']:
        return '#10b981'
    elif status_lower == 'pending':
        return '#f59e0b'
    elif status_lower in ['rejected', 'denied']:
        return '#ef4444'
    else:
        return '#6b7280'

def generate_record_detail_schema(record: Dict[str, Any], community: Optional[str] = None) -> Dict[str, Any]:
    """Generate a UI schema for a single record detail view"""
    
    # Extract record data
    attributes = record.get('attributes', {})
    relationships = record.get('relationships', {})
    
    # Basic record info
    record_number = attributes.get('number', record.get('id', 'Unknown'))
    record_type = attributes.get('typeDescription', 'Building Permit')
    status = attributes.get('status', 'Active')
    
    # Create header schema
    header_schema = {
        "title": record_number,
        "subtitle": record_type,
        "status": {
            "label": status,
            "color": get_status_color(status),
            "icon": "●"
        },
        "metadata": [
            {
                "label": "Applicant",
                "value": "Sethland Greenlaw",  # TODO: Extract from relationships
                "type": "link",
                "icon": "👤"
            },
            {
                "label": "Project",
                "value": attributes.get('projectDescription', 'Mini-Mall - 1234567'),
                "type": "text"
            },
            {
                "label": "Expiration Date",
                "value": format_date(attributes.get('expiresAt')) or '11/21/22',
                "type": "date",
                "icon": "📅"
            },
            {
                "label": "Record Status",
                "value": status,
                "type": "status"
            }
        ]
    }
    
    # Create tabs schema
    tabs_schema = [
        {
            "id": "details",
            "label": "Details",
            "count": None,
            "sections": [
                # Project Information Section
                {
                    "title": "Project Information",
                    "description": "Section level help text or description text",
                    "layout": "grid",
                    "columns": 3,
                    "fields": [
                        {
                            "key": "projectDescription",
                            "label": "Brief Description of Project",
                            "type": "textarea"
                        },
                        {
                            "key": "estimatedCost",
                            "label": "Estimated Project Cost",
                            "type": "currency",
                            "format": {"currency": "USD"}
                        },
                        {
                            "key": "projectType",
                            "label": "Project Type",
                            "type": "text"
                        },
                        {
                            "key": "propertyType",
                            "label": "Property Type",
                            "type": "text"
                        },
                        {
                            "key": "buildDuration",
                            "label": "Build Duration",
                            "type": "text"
                        },
                        {
                            "key": "submittedAt",
                            "label": "Submitted Date",
                            "type": "date"
                        },
                        {
                            "key": "projectID",
                            "label": "Project ID",
                            "type": "text"
                        }
                    ],
                    "actions": [
                        {
                            "id": "edit_project",
                            "label": "Edit",
                            "type": "link",
                            "icon": "✏️"
                        }
                    ]
                },
                # Contractor Information Section
                {
                    "title": "Contractor Information",
                    "layout": "grid",
                    "columns": 2,
                    "fields": [
                        {
                            "key": "contractorRole",
                            "label": "Contractor Role",
                            "type": "text"
                        },
                        {
                            "key": "typeOfWork",
                            "label": "Type of Work",
                            "type": "text"
                        },
                        {
                            "key": "contractorDescription",
                            "label": "Project Description",
                            "type": "textarea"
                        },
                        {
                            "key": "contractorName",
                            "label": "Contractor Name",
                            "type": "text"
                        },
                        {
                            "key": "businessName",
                            "label": "Business Name",
                            "type": "text"
                        }
                    ],
                    "actions": [
                        {
                            "id": "edit_contractor",
                            "label": "Edit",
                            "type": "link",
                            "icon": "✏️"
                        }
                    ]
                },
                # Record Information Section
                {
                    "title": "Record Information",
                    "description": "System and administrative details",
                    "layout": "grid",
                    "columns": 2,
                    "collapsible": True,
                    "defaultExpanded": False,
                    "fields": [
                        {
                            "key": "id",
                            "label": "Record ID",
                            "type": "text",
                            "display": {"color": "#6b7280"}
                        },
                        {
                            "key": "typeID",
                            "label": "Type ID",
                            "type": "text"
                        },
                        {
                            "key": "typeDescription",
                            "label": "Type Description",
                            "type": "text"
                        },
                        {
                            "key": "projectID",
                            "label": "Project ID",
                            "type": "text"
                        },
                        {
                            "key": "isEnabled",
                            "label": "Enabled",
                            "type": "boolean"
                        },
                        {
                            "key": "submittedOnline",
                            "label": "Submitted Online",
                            "type": "boolean"
                        },
                        {
                            "key": "renewalSubmitted",
                            "label": "Renewal Submitted",
                            "type": "boolean"
                        }
                    ]
                },
                # Timeline Section
                {
                    "title": "Timeline",
                    "description": "Important dates and milestones",
                    "layout": "grid",
                    "columns": 2,
                    "fields": [
                        {
                            "key": "createdAt",
                            "label": "Created At",
                            "type": "date"
                        },
                        {
                            "key": "submittedAt",
                            "label": "Submitted At",
                            "type": "date"
                        },
                        {
                            "key": "updatedAt",
                            "label": "Last Updated",
                            "type": "date"
                        },
                        {
                            "key": "expiresAt",
                            "label": "Expires At",
                            "type": "date"
                        }
                    ]
                }
            ],
            "actions": [
                {
                    "id": "request_changes",
                    "label": "Request Changes",
                    "type": "secondary",
                    "icon": "📝"
                }
            ]
        },
        {
            "id": "workflow",
            "label": "Workflow",
            "sections": []
        },
        {
            "id": "attachments",
            "label": "Attachments",
            "count": 7,
            "sections": []
        },
        {
            "id": "location",
            "label": "Location",
            "count": 3,
            "sections": []
        },
        {
            "id": "applicant",
            "label": "Applicant",
            "count": 3,
            "sections": []
        },
        {
            "id": "activity",
            "label": "Activity",
            "sections": []
        }
    ]
    
    # Prepare data with flattened structure and sample data
    data = {
        # Flatten attributes
        **attributes,
        # Add sample data for demo
        "projectDescription": "Building permit will be for a new build at the intersection of Dean Broadway. This will be a multi-unit building and will be about 8000 square feet.",
        "estimatedCost": 20000,
        "projectType": "New Construction",
        "propertyType": "Commercial",
        "buildDuration": "90 days",
        "contractorRole": "General",
        "typeOfWork": "Roofing",
        "contractorDescription": "They're here to take the old shingles off the roof and prep it for the insulation team.",
        "contractorName": "Barry Wilkins",
        "businessName": "Barry's Building Construction Business"
    }
    
    # Create the complete schema
    schema = {
        "type": "detail",
        "header": header_schema,
        "tabs": tabs_schema,
        "data": data,
        "actions": [
            {
                "id": "save_record",
                "label": "Save Changes",
                "type": "primary",
                "icon": "💾"
            },
            {
                "id": "cancel_changes",
                "label": "Cancel",
                "type": "secondary"
            }
        ]
    }
    
    return schema

def generate_records_table_schema(records: List[Dict[str, Any]], community: Optional[str] = None) -> Dict[str, Any]:
    """Generate a UI schema for a records table view"""
    
    # This would be used for table views - keeping the existing SimpleRecordsTable for now
    # as it already handles dynamic column generation well
    
    schema = {
        "type": "table",
        "data": {
            "records": records,
            "community": community
        }
    }
    
    return schema 