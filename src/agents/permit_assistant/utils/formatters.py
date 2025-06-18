"""Formatting utilities for permit data"""

from datetime import datetime
from typing import Dict, List, Any, Optional

def format_date(date_string: Optional[str]) -> Optional[str]:
    """Format date from UTC to local date string"""
    if not date_string:
        return None
    try:
        # Parse the UTC date
        utc_date = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
        # Format as local date (just date part for readability)
        return utc_date.strftime('%Y-%m-%d')
    except:
        return date_string

def get_record_type_name(type_id: Optional[str], type_description: Optional[str], enhanced_relationships: Optional[Dict[str, Any]] = None) -> str:
    """Get a better record type name from ID and description, with optional enhanced relationship data"""
    
    # First check if we have enhanced relationship data from recursive calls
    if enhanced_relationships and "recordType" in enhanced_relationships:
        record_type_rel = enhanced_relationships["recordType"]
        if isinstance(record_type_rel, dict) and "resolved_name" in record_type_rel:
            print(f"🔧 DEBUG: Using resolved record type name from enhanced relationship data: {record_type_rel['resolved_name']}")
            return record_type_rel["resolved_name"]
    
    # Use description if available and not empty
    if type_description and type_description.strip():
        return type_description.strip()
    
    # Otherwise, create a more readable name from typeID
    if type_id:
        # Common permit type mappings (you can expand this based on your data)
        type_mappings = {
            '6413': 'Building Permit',
            '6372': 'Business License', 
            '6370': 'Zoning Permit',
            '6229': 'Temporary Permit',
            '53': 'Special Event Permit'
        }
        return type_mappings.get(str(type_id), f"Permit Type {type_id}")
    
    return "Unknown Type"

def get_address_info(record_data: Dict[str, Any], included_data: List[Dict[str, Any]]) -> Optional[str]:
    """Extract address info from included data or relationships"""
    try:
        # First check if we have locationDetails from MCP server enhancement
        location_details = record_data.get("locationDetails")
        if location_details and isinstance(location_details, dict) and location_details.get("attributes"):
            attrs = location_details["attributes"]
            print(f"🔧 DEBUG: Found enhanced locationDetails for record {record_data.get('id')}: {list(attrs.keys())}")
            
            # Build address from available location attributes
            address_parts = []
            if attrs.get("streetNo"):
                address_parts.append(str(attrs["streetNo"]))
            if attrs.get("streetName"):
                address_parts.append(attrs["streetName"])
            if attrs.get("unit"):
                address_parts.append(f"Unit {attrs['unit']}")
            if attrs.get("city"):
                address_parts.append(attrs["city"])
            if attrs.get("state"):
                address_parts.append(attrs["state"])
            if attrs.get("postalCode"):
                address_parts.append(attrs["postalCode"])
            
            if address_parts:
                return ", ".join(address_parts)
        
        # Fallback to original relationship-based logic
        relationships = record_data.get("relationships", {})
        print(f"🔧 DEBUG: Record {record_data.get('id')} location relationships: {[k for k in relationships.keys() if 'location' in k.lower()]}")
        
        # First check if we have enhanced relationship data from recursive calls
        for key in ["primaryLocation", "location", "address", "site"]:
            if key in relationships:
                location_rel = relationships[key]
                # Check for resolved address from recursive calls
                if isinstance(location_rel, dict) and "resolved_address" in location_rel:
                    print(f"🔧 DEBUG: Using resolved address from enhanced relationship data: {location_rel['resolved_address']}")
                    return location_rel["resolved_address"]
        
        # Try different relationship keys for location
        location_rel = None
        location_key = None
        for key in ["primaryLocation", "location", "address", "site"]:
            if key in relationships:
                location_rel = relationships[key]
                location_key = key
                print(f"🔧 DEBUG: Found location relationship under key '{key}': {location_rel}")
                break
        
        if location_rel:
            # Check if it has data with ID (JSON:API format)
            if "data" in location_rel and location_rel["data"]:
                location_data = location_rel["data"]
                if "id" in location_data:
                    location_id = location_data["id"]
                    location_type = location_data.get("type", "locations")
                    print(f"🔧 DEBUG: Looking for location: id={location_id}, type={location_type}")
                    
                    # Find the location in included data
                    for included_item in included_data:
                        if (included_item.get("type") == location_type and 
                            included_item.get("id") == location_id):
                            location_attrs = included_item.get("attributes", {})
                            print(f"🔧 DEBUG: Found location data: {list(location_attrs.keys())}")
                            
                            # Build address from available location attributes
                            address_parts = []
                            if location_attrs.get("streetNumber"):
                                address_parts.append(str(location_attrs["streetNumber"]))
                            if location_attrs.get("streetName"):
                                address_parts.append(location_attrs["streetName"])
                            if location_attrs.get("city"):
                                address_parts.append(location_attrs["city"])
                            if location_attrs.get("state"):
                                address_parts.append(location_attrs["state"])
                            if location_attrs.get("zipCode"):
                                address_parts.append(location_attrs["zipCode"])
                            
                            # Also try other common address fields
                            if not address_parts:
                                for addr_field in ["address", "fullAddress", "streetAddress"]:
                                    if location_attrs.get(addr_field):
                                        return location_attrs[addr_field]
                            
                            if address_parts:
                                return ", ".join(address_parts)
                            
                            return f"Location {location_id}"
                    
                    # If relationship exists but no included data found
                    return f"Location ID: {location_id}"
            
            # Check if it has direct attributes (non-JSON:API format)
            elif "attributes" in location_rel:
                location_attrs = location_rel["attributes"]
                print(f"🔧 DEBUG: Found direct location attributes: {list(location_attrs.keys())}")
                
                # Build address from available location attributes
                address_parts = []
                if location_attrs.get("streetNumber"):
                    address_parts.append(str(location_attrs["streetNumber"]))
                if location_attrs.get("streetName"):
                    address_parts.append(location_attrs["streetName"])
                if location_attrs.get("city"):
                    address_parts.append(location_attrs["city"])
                if location_attrs.get("state"):
                    address_parts.append(location_attrs["state"])
                if location_attrs.get("zipCode"):
                    address_parts.append(location_attrs["zipCode"])
                
                # Also try other common address fields
                if not address_parts:
                    for addr_field in ["address", "fullAddress", "streetAddress"]:
                        if location_attrs.get(addr_field):
                            return location_attrs[addr_field]
                
                if address_parts:
                    return ", ".join(address_parts)
            
            # Check if it only has links (OpenGov API pattern)
            elif "links" in location_rel:
                print(f"🔧 DEBUG: Location relationship only has links: {location_rel['links']}")
                # Return None instead of placeholder text when only links are available
                return None
            
            # If relationship exists but no usable data, return None
            return None
        
        return None
    except Exception as e:
        print(f"🔧 DEBUG: Error getting address info: {e}")
        return None

def get_owner_email(record_data: Dict[str, Any], included_data: List[Dict[str, Any]]) -> Optional[str]:
    """Get owner email from locationDetails or other sources"""
    try:
        # First check if we have locationDetails from MCP server enhancement
        location_details = record_data.get("locationDetails")
        if location_details and isinstance(location_details, dict) and location_details.get("attributes"):
            attrs = location_details["attributes"]
            if attrs.get("ownerEmail"):
                print(f"🔧 DEBUG: Found owner email in locationDetails for record {record_data.get('id')}: {attrs['ownerEmail']}")
                return attrs["ownerEmail"]
        
        # Fallback to direct ownerEmail field if available
        if record_data.get("ownerEmail"):
            return record_data["ownerEmail"]
        
        # If no owner email, fall back to applicant name as a last resort
        return get_applicant_name(record_data, included_data)
    except Exception as e:
        print(f"🔧 DEBUG: Error getting owner email: {e}")
        return None

def get_applicant_name(record_data: Dict[str, Any], included_data: List[Dict[str, Any]]) -> Optional[str]:
    """Get applicant name from included data or relationships"""
    try:
        relationships = record_data.get("relationships", {})
        print(f"🔧 DEBUG: Record {record_data.get('id')} relationships keys: {list(relationships.keys())}")
        
        # First check if we have enhanced relationship data from recursive calls
        for key in ["applicant", "user", "owner", "primaryContact", "submittedBy"]:
            if key in relationships:
                applicant_rel = relationships[key]
                # Check for resolved name from recursive calls
                if isinstance(applicant_rel, dict) and "resolved_name" in applicant_rel:
                    print(f"🔧 DEBUG: Using resolved name from enhanced relationship data: {applicant_rel['resolved_name']}")
                    return applicant_rel["resolved_name"]
        
        # Try different relationship keys for applicant
        applicant_rel = None
        applicant_key = None
        for key in ["applicant", "user", "owner", "primaryContact", "submittedBy"]:
            if key in relationships:
                applicant_rel = relationships[key]
                applicant_key = key
                print(f"🔧 DEBUG: Found applicant relationship under key '{key}': {applicant_rel}")
                break
        
        if applicant_rel:
            # Check if it has data with ID (JSON:API format)
            if "data" in applicant_rel and applicant_rel["data"]:
                applicant_data = applicant_rel["data"]
                if "id" in applicant_data:
                    applicant_id = applicant_data["id"]
                    applicant_type = applicant_data.get("type", "users")
                    print(f"🔧 DEBUG: Looking for applicant: id={applicant_id}, type={applicant_type}")
                    
                    # Find the applicant in included data
                    for included_item in included_data:
                        if (included_item.get("type") == applicant_type and 
                            included_item.get("id") == applicant_id):
                            applicant_attrs = included_item.get("attributes", {})
                            print(f"🔧 DEBUG: Found applicant data: {list(applicant_attrs.keys())}")
                            
                            # Build name from available attributes
                            name_parts = []
                            if applicant_attrs.get("firstName"):
                                name_parts.append(applicant_attrs["firstName"])
                            if applicant_attrs.get("lastName"):
                                name_parts.append(applicant_attrs["lastName"])
                            
                            if name_parts:
                                return " ".join(name_parts)
                            
                            # Fallback to other name fields
                            for name_field in ["name", "displayName", "fullName", "email"]:
                                if applicant_attrs.get(name_field):
                                    return applicant_attrs[name_field]
                            
                            return f"User {applicant_id}"
                    
                    # If relationship exists but no included data found
                    return f"Applicant ID: {applicant_id}"
            
            # Check if it has direct attributes (non-JSON:API format)
            elif "attributes" in applicant_rel:
                applicant_attrs = applicant_rel["attributes"]
                print(f"🔧 DEBUG: Found direct applicant attributes: {list(applicant_attrs.keys())}")
                
                # Build name from available attributes
                name_parts = []
                if applicant_attrs.get("firstName"):
                    name_parts.append(applicant_attrs["firstName"])
                if applicant_attrs.get("lastName"):
                    name_parts.append(applicant_attrs["lastName"])
                
                if name_parts:
                    return " ".join(name_parts)
                
                # Fallback to other name fields
                for name_field in ["name", "displayName", "fullName", "email"]:
                    if applicant_attrs.get(name_field):
                        return applicant_attrs[name_field]
            
            # Check if it only has links (OpenGov API pattern)
            elif "links" in applicant_rel:
                print(f"🔧 DEBUG: Applicant relationship only has links: {applicant_rel['links']}")
                # Return None instead of placeholder text when only links are available
                return None
            
            # If relationship exists but no usable data, return None
            return None
        
        return None
    except Exception as e:
        print(f"🔧 DEBUG: Error getting applicant name: {e}")
        return None 