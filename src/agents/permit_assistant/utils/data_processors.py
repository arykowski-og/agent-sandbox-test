"""Data processing utilities for UI components"""

from typing import List, Dict, Any
from .formatters import format_date, get_record_type_name, get_address_info, get_applicant_name

def process_records_for_ui(records: List[Dict[str, Any]], included_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Process records to ensure proper field mapping for UI components"""
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
    
    return processed_records 