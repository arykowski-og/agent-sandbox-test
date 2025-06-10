#!/usr/bin/env python3
"""Test script for schema generation"""

import json
from schema_generator import generate_record_detail_schema

# Sample OpenGov record data
sample_record = {
    "id": "12345",
    "type": "record",
    "attributes": {
        "number": "BP-2024-001234",
        "histID": None,
        "histNumber": None,
        "typeID": "BP",
        "typeDescription": "Building Permit",
        "projectID": "PROJ-2024-5678",
        "projectDescription": "New Commercial Building",
        "status": "Active",
        "isEnabled": True,
        "submittedAt": "2024-01-15T10:30:00Z",
        "expiresAt": "2024-12-15T23:59:59Z",
        "renewalOfRecordID": None,
        "renewalNumber": None,
        "submittedOnline": True,
        "renewalSubmitted": False,
        "createdAt": "2024-01-15T10:30:00Z",
        "updatedAt": "2024-01-16T14:22:00Z",
        "createdBy": "system",
        "updatedBy": "admin"
    },
    "relationships": {
        "applicant": {"links": {"related": "/api/applicants/123"}},
        "primaryLocation": {"links": {"related": "/api/locations/456"}}
    }
}

def test_schema_generation():
    """Test the schema generation"""
    print("Testing schema generation...")
    
    try:
        schema = generate_record_detail_schema(sample_record, "Newton, MA")
        
        print(f"✅ Schema generated successfully!")
        print(f"   - Type: {schema['type']}")
        print(f"   - Header title: {schema['header']['title']}")
        print(f"   - Number of tabs: {len(schema['tabs'])}")
        print(f"   - Number of actions: {len(schema['actions'])}")
        
        # Print first tab details
        if schema['tabs']:
            first_tab = schema['tabs'][0]
            print(f"   - First tab: {first_tab['label']} with {len(first_tab['sections'])} sections")
            
            if first_tab['sections']:
                first_section = first_tab['sections'][0]
                print(f"   - First section: {first_section['title']} with {len(first_section['fields'])} fields")
        
        # Save to file for inspection
        with open('sample_schema.json', 'w') as f:
            json.dump(schema, f, indent=2)
        print("   - Schema saved to sample_schema.json")
        
        return True
        
    except Exception as e:
        print(f"❌ Schema generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_schema_generation()
    exit(0 if success else 1) 